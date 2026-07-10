import json
import httpx
from app.config import settings


EXTRACTION_PROMPT = """You are a resume analyzer. Read the resume below and extract key facts about the candidate.
Return a JSON object with these keys:
- "summary": a 3-5 sentence professional summary
- "top_skills": a list of the candidate's strongest technical or professional skills
- "key_experiences": a list of 2-4 notable work/project experiences with one sentence each
- "years_of_experience": approximate total years of experience as a string (e.g. "5+ years")
- "education": highest relevant education

Resume:
{resume_text}

Return only valid JSON."""


async def extract_resume_facts(resume_text: str) -> dict:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")
    if not resume_text or not resume_text.strip():
        return {
            "summary": "",
            "top_skills": [],
            "key_experiences": [],
            "years_of_experience": "",
            "education": "",
        }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.LLM_MODEL or "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You extract structured facts from resumes."},
                    {"role": "user", "content": EXTRACTION_PROMPT.format(resume_text=resume_text)},
                ],
                "temperature": 0.2,
                "max_tokens": 700,
                "response_format": {"type": "json_object"},
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
        return json.loads(content)


def format_resume_summary(facts: dict) -> str:
    lines = [
        f"Summary: {facts.get('summary', '')}",
        f"Top skills: {', '.join(facts.get('top_skills', []))}",
        f"Years of experience: {facts.get('years_of_experience', '')}",
        f"Education: {facts.get('education', '')}",
        "Key experiences:",
    ]
    for exp in facts.get("key_experiences", []):
        lines.append(f"- {exp}")
    return "\n".join(lines)
