import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./interview_copilot.db"
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    ASR_PROVIDER: str = "deepgram"
    DEEPGRAM_API_KEY: str | None = None
    ASSEMBLYAI_API_KEY: str | None = None

    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o-mini"

    MOCK_ASR: bool = False
    MOCK_LLM: bool = False

    FRONTEND_ORIGIN: str = "http://localhost:3000"

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")


settings = Settings()
