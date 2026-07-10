from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import auth, profiles, sessions, audio

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Interview Copilot API",
    description="Real-time AI interview copilot backend",
    version="0.1.0",
)

origins = ["*"] if settings.FRONTEND_ORIGIN == "*" else [settings.FRONTEND_ORIGIN]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(sessions.router)
app.include_router(audio.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
