import json
import httpx
from app.config import settings


LENGTH_INSTRUCTIONS = {
    "short": "Keep the answer concise: 1-2 sentences or 30-60 seconds spoken.",
    "medium": "Keep the answer moderate: 2-4 sentences or 60-90 seconds spoken.",
    "long": "Provide a thorough answer: 4-6 sentences or 1-2 minutes spoken.",
}


TONE_INSTRUCTIONS = {
    "professional": "Use a professional, polished tone.",
    "casual": "Use a friendly, conversational tone.",
    "technical": "Use a precise, technical tone with relevant terminology.",
    "confident": "Use a confident, assertive tone.",
}


class OpenAILLM:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY or ""
        self.model = settings.LLM_MODEL

    def _build_prompts(self, profile: dict, question: str):
        tone = TONE_INSTRUCTIONS.get(profile.get("tone", "professional"), "")
        length = LENGTH_INSTRUCTIONS.get(profile.get("answer_length", "medium"), "")

        system_prompt = f"""You are an expert interview coach. Help the candidate answer the interview question.
Use the provided profile, resume summary, and job description to tailor the answer.
{tone}
{length}
Answer as if the candidate is speaking. Do not include greetings or sign-offs."""

        user_prompt = f"""Role: {profile.get('role_title', '')}
Target company: {profile.get('target_company', '')}

About me:
{profile.get('about_me', '')}

Key strengths:
{profile.get('key_strengths', '')}

Resume summary:
{profile.get('resume_summary', '')}

Full resume:
{profile.get('resume_text', '')}

Job description:
{profile.get('job_description', '')}

Sample answers in my voice (match this style):
{profile.get('sample_answers', '')}

Question: {question}

Suggested answer:"""

        return system_prompt, user_prompt

    async def generate_answer(self, profile: dict, question: str) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        system_prompt, user_prompt = self._build_prompts(profile, question)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    async def generate_answer_stream(self, profile: dict, question: str):
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        system_prompt, user_prompt = self._build_prompts(profile, question)

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "stream": True,
                },
                timeout=30.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line or line.startswith(":"):
                        continue
                    if line == "data: [DONE]":
                        break
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, IndexError, KeyError):
                            continue

    async def generate_answer_stream_with_vision(self, profile: dict, question: str, image_base64: str):
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        system_prompt, user_prompt = self._build_prompts(profile, question)
        vision_system_prompt = system_prompt + "\nA screenshot from the meeting is also provided. Use the visual context to improve the answer when relevant."

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": vision_system_prompt},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}",
                                        "detail": "low",
                                    },
                                },
                            ],
                        },
                    ],
                    "temperature": 0.7,
                    "max_tokens": 700,
                    "stream": True,
                },
                timeout=45.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line or line.startswith(":"):
                        continue
                    if line == "data: [DONE]":
                        break
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, IndexError, KeyError):
                            continue


class AnthropicLLM:
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY or ""
        self.model = "claude-3-5-sonnet-20240620"

    async def generate_answer(self, profile: dict, question: str) -> str:
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")

        tone = TONE_INSTRUCTIONS.get(profile.get("tone", "professional"), "")
        length = LENGTH_INSTRUCTIONS.get(profile.get("answer_length", "medium"), "")

        system_prompt = f"""You are an expert interview coach. Help the candidate answer the interview question.
Use the provided resume and job description to tailor the answer.
{tone}
{length}
Answer as if the candidate is speaking. Do not include greetings or sign-offs."""

        user_prompt = f"""Role: {profile.get('role_title', '')}
Target company: {profile.get('target_company', '')}
Resume:
{profile.get('resume_text', '')}

Job description:
{profile.get('job_description', '')}

Question: {question}

Suggested answer:"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": self.model,
                    "max_tokens": 500,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"].strip()


async def generate_answer(profile: dict, question: str) -> str:
    if settings.MOCK_LLM:
        return (
            f"[MOCK] Tailored answer for {profile.get('role_title', 'role')} at "
            f"{profile.get('target_company', 'company')}: here's a concise response to '{question}'."
        )
    provider = settings.LLM_PROVIDER.lower()
    if provider == "openai":
        llm = OpenAILLM()
    elif provider == "anthropic":
        llm = AnthropicLLM()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    return await llm.generate_answer(profile, question)


async def generate_answer_stream(profile: dict, question: str):
    if settings.MOCK_LLM:
        yield (
            f"[MOCK] Tailored answer for {profile.get('role_title', 'role')} at "
            f"{profile.get('target_company', 'company')}: here's a concise response to '{question}'."
        )
        return
    provider = settings.LLM_PROVIDER.lower()
    if provider == "openai":
        llm = OpenAILLM()
        async for token in llm.generate_answer_stream(profile, question):
            yield token
    else:
        raise ValueError("Streaming is currently only supported with OpenAI.")


async def generate_answer_stream_with_vision(profile: dict, question: str, image_base64: str):
    if settings.MOCK_LLM:
        yield (
            f"[MOCK + VISION] Tailored answer for {profile.get('role_title', 'role')} at "
            f"{profile.get('target_company', 'company')} using screen context: concise response to '{question}'."
        )
        return
    provider = settings.LLM_PROVIDER.lower()
    if provider == "openai":
        llm = OpenAILLM()
        async for token in llm.generate_answer_stream_with_vision(profile, question, image_base64):
            yield token
    else:
        raise ValueError("Vision streaming is currently only supported with OpenAI.")
