# Sharing Pardha with Friends

This guide helps you share the app with 1–3 friends so they can run it locally on Mac or Windows and test it for you.

> **Note:** For testing, your friends can use your API keys. Share them securely outside of GitHub (e.g., iMessage, Signal, or a password manager). Do not commit API keys to the repo.

---

## 1. Give them access to the code

Share the GitHub repository URL for Pardha:

```
https://github.com/Raja849269956/pardha
```

They should clone it to their computer:

```bash
git clone https://github.com/Raja849269956/pardha.git
cd pardha
```

---

## 2. Prerequisites

### All users

- A free GitHub account (to clone the repo)
- OpenAI API key with billing enabled (the owner can share theirs for testing)
- Deepgram API key (the owner can share theirs for testing)

### Mac

- macOS 11 (Big Sur) or newer
- Homebrew recommended
- Python 3.10+
- Node.js 18+
- BlackHole 16ch virtual audio driver

### Windows

- Windows 10 or Windows 11
- Python 3.10+ (from python.org or Microsoft Store)
- Node.js 18+ (from nodejs.org)
- Git for Windows
- A virtual audio cable such as VB-Cable or VoiceMeeter Banana

---

## 3. Backend setup

### 3.1 Create virtual environment

**Mac:**

```bash
cd interview-copilot/backend
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**

```powershell
cd interview-copilot\backend
python -m venv .venv
.venv\Scripts\activate
```

### 3.2 Install dependencies

```bash
pip install -r requirements.txt
```

### 3.3 Create the `.env` file

Copy the example file and fill in the API keys:

```bash
cp .env.example .env
```

**Windows:**

```powershell
copy .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=sqlite:///./interview_copilot.db
SECRET_KEY=any-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

OPENAI_API_KEY=sk-your-openai-key
DEEPGRAM_API_KEY=your-deepgram-key

LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
ASR_PROVIDER=deepgram

MOCK_ASR=false
MOCK_LLM=false

FRONTEND_ORIGIN=http://localhost:3000
```

### 3.4 Run the backend

```bash
uvicorn app.main:app --reload
```

The backend runs at `http://localhost:8000`.

---

## 4. Desktop app setup

Open a second terminal.

### 4.1 Install dependencies

**Mac:**

```bash
cd interview-copilot/desktop
npm install
```

**Windows:**

```powershell
cd interview-copilot\desktop
npm install
```

### 4.2 Create the `.env` file

```bash
cp .env.example .env
```

**Windows:**

```powershell
copy .env.example .env
```

Edit `.env`:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

### 4.3 Run the desktop app

**Mac:**

```bash
npm run dev
```

**Windows:**

```powershell
npm run dev
```

The Electron app should open.

---

## 5. Audio routing setup

### Mac

1. Install **BlackHole 16ch** from https://github.com/ExistentialAudio/BlackHole
2. Open **Audio MIDI Setup** (search in Spotlight)
3. Create a **Multi-Output Device**
4. Check both **MacBook Speakers** and **BlackHole 16ch**
5. Set the Multi-Output Device as the system output
6. In the Interview Copilot app, select **BlackHole 16ch** as the audio input

### Windows

1. Install **VB-Cable** (free) or **VoiceMeeter Banana** from https://vb-audio.com/
2. Set the virtual cable as the default playback device
3. In the Interview Copilot app, select the virtual cable as the audio input
4. If using VoiceMeeter, route the virtual cable output to your real speakers/headphones so you can still hear the interview

> **Tip:** Your friends should test with music or a YouTube video first to confirm the app is hearing the system audio.

---

## 6. First run test

1. Register a new account in the app (it stores locally in SQLite)
2. Create a profile:
   - Paste their resume
   - Fill in role, target company, about me, key strengths
   - Click **Extract Resume Facts** (optional but recommended)
3. Start a session
4. Play an interview question from YouTube or speak into the mic
5. The overlay should appear with a live transcript and suggested answer

---

## 7. Important notes

- **API costs:** Each question answered uses OpenAI tokens. Since your friends are using your keys, usage will count against your account. Monitor your OpenAI/Deepgram usage.
- **Screen capture protection:** The overlay is hidden from screen capture on macOS. On Windows this may behave differently depending on the capture method.
- **No packaged app yet:** They must run from source using the steps above.
- **Do not commit `.env` files:** Make sure they never run `git add .env` or push API keys.

---

## 8. Troubleshooting

### Backend fails to start

- Check Python version: `python --version` should be 3.10+
- Make sure `.venv` is activated
- Make sure `.env` has valid API keys

### No transcription

- Confirm the correct audio input is selected
- Confirm BlackHole / virtual cable is receiving audio
- Check backend logs for Deepgram errors

### No answer appears

- Check backend logs for OpenAI errors
- Make sure OpenAI billing is active
- Check that `MOCK_LLM=false` in `.env`

---

## 9. Quick command reference

| Task | Mac | Windows |
|------|-----|---------|
| Activate venv | `source .venv/bin/activate` | `.venv\Scripts\activate` |
| Run backend | `uvicorn app.main:app --reload` | `uvicorn app.main:app --reload` |
| Run desktop | `npm run dev` | `npm run dev` |
| Copy .env | `cp .env.example .env` | `copy .env.example .env` |
