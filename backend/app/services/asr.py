import os
import json
import asyncio
from typing import Callable
import httpx
import websockets

from app.config import settings


class TranscriptionHandler:
    def __init__(self, on_transcript: Callable[[str, bool], None]):
        self.on_transcript = on_transcript
        self.buffer = ""

    async def handle(self, transcript: str, is_final: bool):
        if is_final:
            self.buffer = transcript
            await self.on_transcript(transcript, is_final=True)
        else:
            await self.on_transcript(transcript, is_final=False)


class DeepgramASR:
    def __init__(self):
        self.api_key = settings.DEEPGRAM_API_KEY or ""

    async def stream(self, audio_queue: asyncio.Queue, handler: TranscriptionHandler):
        if not self.api_key:
            raise RuntimeError("DEEPGRAM_API_KEY is not set")

        url = (
            "wss://api.deepgram.com/v1/listen?"
            "encoding=linear16&sample_rate=16000&channels=1&"
            "punctuate=true&interim_results=true&language=en&"
            "endpointing=100"
        )
        headers = {"Authorization": f"Token {self.api_key}"}

        async with websockets.connect(url, extra_headers=headers) as ws:
            async def send_audio():
                while True:
                    chunk = await audio_queue.get()
                    if chunk is None:
                        await ws.send(json.dumps({"type": "CloseStream"}))
                        break
                    await ws.send(chunk)

            async def receive_transcripts():
                async for message in ws:
                    data = json.loads(message)
                    if "channel" in data:
                        alternatives = data["channel"]["alternatives"]
                        if alternatives:
                            alt = alternatives[0]
                            transcript = alt.get("transcript", "")
                            is_final = data.get("is_final", False)
                            if transcript:
                                await handler.handle(transcript, is_final)
                    if data.get("type") == "UtteranceEnd":
                        await handler.handle("", is_final=True)

            send_task = asyncio.create_task(send_audio())
            try:
                await receive_transcripts()
            finally:
                send_task.cancel()
                try:
                    await send_task
                except asyncio.CancelledError:
                    pass


class AssemblyAIASR:
    def __init__(self):
        self.api_key = settings.ASSEMBLYAI_API_KEY or ""

    async def stream(self, audio_queue: asyncio.Queue, handler: TranscriptionHandler):
        # AssemblyAI real-time streaming requires a separate websocket connection
        # initiated through their SDK. This is a placeholder implementation.
        raise NotImplementedError("AssemblyAI streaming not yet implemented")


class MockASR:
    async def stream(self, audio_queue: asyncio.Queue, handler: TranscriptionHandler):
        while True:
            item = await audio_queue.get()
            if item is None:
                break
            if isinstance(item, str):
                await handler.handle(item, is_final=True)


async def create_asr_stream(audio_queue: asyncio.Queue, handler: TranscriptionHandler):
    if settings.MOCK_ASR:
        asr = MockASR()
    elif settings.ASR_PROVIDER.lower() == "deepgram":
        asr = DeepgramASR()
    elif settings.ASR_PROVIDER.lower() == "assemblyai":
        asr = AssemblyAIASR()
    else:
        raise ValueError(f"Unsupported ASR provider: {settings.ASR_PROVIDER}")
    await asr.stream(audio_queue, handler)
