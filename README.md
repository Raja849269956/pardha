# Pardha

Advanced real-time AI interview copilot. Captures live meeting audio, reads shared screens, and surfaces personalized answer suggestions in a private overlay.

> This is a fork of Interview Copilot with advanced features under active development.

## Advanced features

- **Screen-aware answers** — When someone shares their screen in Teams/Meet/Zoom, Pardha captures it and uses the visual context to answer questions about slides, code, or diagrams.
- **Streaming answers** — Suggestions appear word-by-word instead of waiting for the full response.
- **Profile memory** — Resume extraction, key strengths, about me, and sample answers make responses sound like you.

## Architecture

- **Backend**: FastAPI + SQLAlchemy + SQLite (default) / PostgreSQL (production) + JWT auth.
- **AI**: Deepgram streaming ASR + OpenAI/Anthropic LLM.
- **Desktop**: Electron + React + WebSocket client.
- **Audio capture**: Virtual audio driver (BlackHole on macOS, VB-Cable on Windows).

## Project layout

```
pardha/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   └── services/
│   ├── requirements.txt
│   └── .env.example
└── desktop/          # Electron + React desktop app
    ├── src/
    │   ├── main.js
    │   ├── preload.js
    │   └── renderer/
    ├── package.json
    └── .env.example
```

## Quick start

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env:
#   - SECRET_KEY (generate a random 32+ char key)
#   - OPENAI_API_KEY or ANTHROPIC_API_KEY
#   - DEEPGRAM_API_KEY (or set ASR_PROVIDER to openai/assemblyai)

uvicorn app.main:app --reload
```

The backend defaults to SQLite for local development. For PostgreSQL, set `DATABASE_URL=postgresql://...` and install `psycopg2-binary`.

### Desktop

```bash
cd desktop
npm install
cp .env.example .env
# Edit .env to point at your backend:
#   REACT_APP_API_URL=http://localhost:8000
#   REACT_APP_WS_URL=ws://localhost:8000

npm run dev
```

## Usage flow

1. **Register / login** in the desktop app.
2. **Create a profile** with resume, job description, role, company, tone, and answer length.
3. **Start a session** from a profile.
4. **Select the virtual audio input** (e.g., BlackHole) and click **Start Listening**.
5. The overlay appears automatically; transcripts and answer suggestions stream in real time.
6. Click **Stop & End Session** to close the overlay and save history.

## Audio setup

1. Install a virtual audio driver:
   - macOS: [BlackHole](https://github.com/ExistentialAudio/BlackHole) (multi-output device recommended)
   - Windows: [VB-Cable](https://vb-audio.com/Cable/) or [Voicemeeter](https://vb-audio.com/Voicemeeter/)
2. Route your meeting app (Zoom/Meet/Teams) output to the virtual speaker.
3. In the copilot, select the virtual microphone as input.

## API endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/profiles/` / `POST` / `PUT` / `DELETE`
- `GET /api/v1/sessions/` / `POST` / `GET /{id}` / `POST /{id}/end` / `DELETE`
- `WS /api/v1/audio/{session_id}` — first message must be `{"type":"auth","token":"..."}`

## WebSocket messages

Incoming from server:

- `transcript` — interim or final transcript text.
- `question_detected` — a question was detected.
- `suggestion` — generated answer suggestion.
- `error` — server error.

## Environment variables

See `.env.example` in both `backend/` and `desktop/` for all options.

## Testing without API keys

Set `MOCK_ASR=true` and `MOCK_LLM=true` in `backend/.env` to test the full WebSocket flow without Deepgram/OpenAI/Anthropic keys. In mock mode, send text messages to the audio WebSocket:

```json
{"type": "mock_audio", "payload": "Tell me about yourself?"}
```

The server will respond with `transcript`, `question_detected`, and `suggestion` messages.

## Known limitations / next steps

- ASR/LLM require valid API keys in production (or use mock mode for testing).
- System audio capture on macOS requires a virtual audio driver.
- The overlay is currently a local Electron window only.
- Suggestions are generated automatically with a cooldown; manual trigger could be added.

## License

MIT
