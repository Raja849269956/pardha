from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class ProfileCreate(BaseModel):
    name: str
    role_title: str
    target_company: Optional[str] = None
    resume_text: Optional[str] = None
    job_description: Optional[str] = None
    about_me: Optional[str] = None
    key_strengths: Optional[str] = None
    sample_answers: Optional[str] = None
    tone: str = "professional"
    answer_length: str = "medium"


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    role_title: Optional[str] = None
    target_company: Optional[str] = None
    resume_text: Optional[str] = None
    resume_summary: Optional[str] = None
    job_description: Optional[str] = None
    about_me: Optional[str] = None
    key_strengths: Optional[str] = None
    sample_answers: Optional[str] = None
    tone: Optional[str] = None
    answer_length: Optional[str] = None


class ProfileOut(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    role_title: str
    target_company: Optional[str]
    resume_text: Optional[str]
    resume_summary: Optional[str]
    job_description: Optional[str]
    about_me: Optional[str]
    key_strengths: Optional[str]
    sample_answers: Optional[str]
    tone: str
    answer_length: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    profile_id: UUID
    name: Optional[str] = None


class SessionOut(BaseModel):
    id: UUID
    user_id: UUID
    profile_id: Optional[UUID]
    name: Optional[str]
    is_active: bool
    created_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True


class TranscriptOut(BaseModel):
    id: UUID
    session_id: UUID
    speaker: str
    text: str
    is_question: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SuggestionOut(BaseModel):
    id: UUID
    session_id: UUID
    question_text: str
    answer_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class AudioStreamMessage(BaseModel):
    type: str
    payload: dict
