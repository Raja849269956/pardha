import asyncio
import json
import time
from datetime import datetime
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app import models, auth as auth_utils
from app.config import settings
from app.services.asr import TranscriptionHandler, create_asr_stream
from app.services.question_detector import QuestionDetector
from app.services.llm import generate_answer, generate_answer_stream, generate_answer_stream_with_vision

router = APIRouter(prefix="/api/v1/audio", tags=["audio"])
logger = logging.getLogger(__name__)


async def get_user_from_token(token: str, db: Session) -> models.User:
    try:
        payload = auth_utils.decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.websocket("/{session_id}")
async def audio_stream(websocket: WebSocket, session_id: str):
    db = next(get_db())
    await websocket.accept()

    try:
        # First message must contain auth token
        auth_message = await websocket.receive_text()
        auth_data = json.loads(auth_message)
        token = auth_data.get("token")
        if not token:
            await websocket.close(code=4001)
            return

        user = await get_user_from_token(token, db)
        session = db.query(models.Session).filter(
            models.Session.id == session_id,
            models.Session.user_id == user.id,
        ).first()
        if not session:
            await websocket.close(code=4004)
            return

        profile = session.profile
        if not profile:
            await websocket.close(code=4004)
            return

        profile_dict = {
            "role_title": profile.role_title,
            "target_company": profile.target_company,
            "resume_text": profile.resume_text,
            "resume_summary": profile.resume_summary,
            "job_description": profile.job_description,
            "about_me": profile.about_me,
            "key_strengths": profile.key_strengths,
            "sample_answers": profile.sample_answers,
            "tone": profile.tone,
            "answer_length": profile.answer_length,
        }

        audio_queue: asyncio.Queue = asyncio.Queue()
        detector = QuestionDetector(cooldown_seconds=2.0)
        current_question = None
        streaming_question = None
        latest_screen_image = None

        async def stream_answer(question: str):
            nonlocal streaming_question, latest_screen_image
            streaming_question = question
            full_answer = ""
            screen_image = latest_screen_image
            latest_screen_image = None  # consume it for this question

            await websocket.send_text(json.dumps({
                "type": "suggestion_start",
                "payload": {"question": question}
            }))

            try:
                answer_stream = (
                    generate_answer_stream_with_vision(profile_dict, question, screen_image)
                    if screen_image
                    else generate_answer_stream(profile_dict, question)
                )
                async for token in answer_stream:
                    full_answer += token
                    await websocket.send_text(json.dumps({
                        "type": "suggestion_token",
                        "payload": {"token": token}
                    }))
            except Exception as e:
                error_token = f"[Error generating answer: {str(e)}]"
                full_answer += error_token
                await websocket.send_text(json.dumps({
                    "type": "suggestion_token",
                    "payload": {"token": error_token}
                }))

            db_suggestion = models.Suggestion(
                session_id=session_id,
                question_text=question,
                answer_text=full_answer,
            )
            db.add(db_suggestion)
            db.commit()

            await websocket.send_text(json.dumps({
                "type": "suggestion_end",
                "payload": {"question": question, "answer": full_answer}
            }))
            streaming_question = None

        async def on_transcript(transcript: str, is_final: bool):
            nonlocal current_question
            if not transcript.strip():
                return

            # Persist final transcript
            if is_final:
                db_transcript = models.Transcript(
                    session_id=session_id,
                    speaker="interviewer",
                    text=transcript,
                    is_question=False,
                )
                db.add(db_transcript)
                db.commit()

                await websocket.send_text(json.dumps({
                    "type": "transcript",
                    "payload": {
                        "text": transcript,
                        "is_final": True,
                        "is_question": False,
                    }
                }))

                if streaming_question is None and detector.detect(transcript, time.time()):
                    current_question = transcript
                    await websocket.send_text(json.dumps({
                        "type": "question_detected",
                        "payload": {"text": transcript}
                    }))
                    asyncio.create_task(stream_answer(transcript))
            else:
                await websocket.send_text(json.dumps({
                    "type": "transcript",
                    "payload": {
                        "text": transcript,
                        "is_final": False,
                        "is_question": False,
                    }
                }))

        handler = TranscriptionHandler(on_transcript)

        asr_task = asyncio.create_task(create_asr_stream(audio_queue, handler))

        async def handle_incoming(raw):
            nonlocal latest_screen_image
            if isinstance(raw, str):
                try:
                    data = json.loads(raw)
                    msg_type = data.get("type")
                    if msg_type == "mock_audio" and settings.MOCK_ASR:
                        await audio_queue.put(data.get("payload", ""))
                    elif msg_type == "screen_context":
                        latest_screen_image = data.get("payload", {}).get("image_base64")
                except json.JSONDecodeError:
                    if settings.MOCK_ASR:
                        await audio_queue.put(raw)
            elif isinstance(raw, bytes):
                await audio_queue.put(raw)

        try:
            while True:
                data = await websocket.receive()
                msg_type = data.get("type")
                if msg_type == "websocket.disconnect":
                    break
                if msg_type == "websocket.receive":
                    if "text" in data:
                        await handle_incoming(data["text"])
                    elif "bytes" in data:
                        await handle_incoming(data["bytes"])
        except WebSocketDisconnect:
            pass
        finally:
            await audio_queue.put(None)
            asr_task.cancel()
            try:
                await asr_task
            except asyncio.CancelledError:
                pass

    except Exception as e:
        logger.exception(f"Audio stream error: {e}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "payload": {"message": str(e)}
            }))
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
