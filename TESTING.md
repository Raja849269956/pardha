# Pardha — QA / Tester Guide

This guide explains how to set up and test the Pardha MVP on a local machine.

## Test setup

### 1. Prerequisites

- macOS or Windows
- Python 3.11+ (`python3 --version`)
- Node.js 18+ (`node --version`)
- Git

### 2. Project location

```
/Users/rajanarenderreddylingaladinne/CascadeProjects/interview-copilot
```

## Backend setup

### 1. Open a terminal and go to the backend folder

```bash
cd /Users/rajanarenderreddylingaladinne/CascadeProjects/interview-copilot/backend
```

### 2. Create the virtual environment (first time only)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the `.env` file

```bash
cp .env.example .env
```

Edit `.env` in your editor.

**For testing without paid AI keys:**

```
SECRET_KEY=<paste-generated-key>
MOCK_ASR=true
MOCK_LLM=true
```

Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**For real AI testing:**

```
SECRET_KEY=<paste-generated-key>
MOCK_ASR=false
MOCK_LLM=false
OPENAI_API_KEY=sk-...
DEEPGRAM_API_KEY=...
```

### 5. Start the backend

```bash
uvicorn app.main:app --reload
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6. Verify backend is healthy

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"ok"}
```

## Desktop app setup

### 1. Open a second terminal and go to the desktop folder

```bash
cd /Users/rajanarenderreddylingaladinne/CascadeProjects/interview-copilot/desktop
```

### 2. Install Node dependencies (first time only)

```bash
npm install
```

### 3. Create the desktop `.env` file

```bash
cp .env.example .env
```

Defaults are fine for local testing:

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

### 4. Start the desktop app

```bash
npm run dev
```

Two windows should appear:

1. **Main window** — login, profiles, sessions.
2. **Overlay window** — floating transcript and suggestions.

## Manual test cases

### Test 1: Register a new user

1. In the desktop app, click **Register**.
2. Enter an email and password.
3. Click **Register**.

Expected: You are logged in and redirected to the Profiles screen.

### Test 2: Create a profile

1. On the Profiles screen, fill in:
   - Profile name
   - Role title
   - Target company
   - Resume text
   - Job description
   - Tone (professional / casual / technical / confident)
   - Answer length (short / medium / long)
2. Click **Create**.

Expected: The profile appears in the list.

### Test 3: Start a session

1. Click **Start Session** on a profile.
2. (Optional) Enter a session name.
3. Click **Start Capturing**.

Expected: The Audio Capture screen opens and the overlay window appears.

### Test 4: Mock audio test (no API keys needed)

When `MOCK_ASR=true` and `MOCK_LLM=true`:

1. In the Audio Capture screen, select any audio input.
2. Click **Start Listening**.
3. Send a mock audio message using the command below in a terminal:

```bash
python3 - <<'PY'
import asyncio, json, websockets

TOKEN = "<paste-token-from-login>"
SESSION_ID = "<paste-session-id>"

async def test():
    async with websockets.connect(f"ws://localhost:8000/api/v1/audio/{SESSION_ID}") as ws:
        await ws.send(json.dumps({"type": "auth", "token": TOKEN}))
        await ws.send(json.dumps({"type": "mock_audio", "payload": "Tell me about yourself?"}))
        for _ in range(5):
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            print(msg)

asyncio.run(test())
PY
```

To get a token:

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=<your-email>&password=<your-password>"
```

To get a session ID:

```bash
curl -s http://localhost:8000/api/v1/sessions/ \
  -H "Authorization: Bearer <paste-token>"
```

Expected messages:

- `transcript` — contains the question text.
- `question_detected` — confirms a question was detected.
- `suggestion` — contains a generated answer.

### Test 5: Real audio test

1. Install a virtual audio driver:
   - macOS: [BlackHole](https://github.com/ExistentialAudio/BlackHole)
   - Windows: [VB-Cable](https://vb-audio.com/Cable/)
2. Set Zoom/Meet/Teams output to the virtual speaker.
3. In the copilot, select the virtual microphone as input.
4. Click **Start Listening**.
5. Speak or play interview audio.

Expected:

- Transcript text appears in the Audio Capture screen.
- Questions trigger answer suggestions in the overlay.

### Test 6: End session

1. Click **Stop & End Session**.

Expected: The overlay closes and the session is saved.

## Common issues

| Issue | Fix |
|-------|-----|
| `python3` not found | Install Python 3.11+ from python.org |
| `node` not found | Install Node.js 18+ from nodejs.org |
| `pip install` fails | Upgrade pip: `pip install --upgrade pip` |
| Port 8000 already in use | Kill it: `lsof -ti:8000 \| xargs kill -9` |
| Electron window does not open | Make sure you are on macOS/Windows with a GUI session |
| No transcript appears | Check that the correct microphone is selected and that audio is being captured |

## What to report

For each test, report:

- Pass / Fail
- Screenshot if the UI looks wrong
- Exact error message if a command or API call fails
- Browser/Electron logs if available

## Files and logs

- Backend logs: terminal running `uvicorn`
- Desktop logs: terminal running `npm run dev`
- Database: `backend/interview_copilot.db` (SQLite)
