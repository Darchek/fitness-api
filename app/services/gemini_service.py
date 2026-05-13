import asyncio
from typing import Optional

from google import genai

from app.core.config import settings
from app.prompts.gemini_prompts import SYSTEM_PROMPT


class GeminiService:
    @staticmethod
    def _get_client() -> genai.Client:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured")
        return genai.Client(api_key=settings.GEMINI_API_KEY)

    @staticmethod
    def _build_contents(prompt: str, system_prompt: Optional[str] = None) -> str:
        active_system_prompt = system_prompt or SYSTEM_PROMPT
        return f"{active_system_prompt}\n\n{prompt}"

    @classmethod
    def generate_text_sync(
        cls,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        client = cls._get_client()
        response = client.models.generate_content(
            model=model or settings.GEMINI_MODEL,
            contents=cls._build_contents(prompt, system_prompt),
        )
        return response.text or ""

    @classmethod
    async def generate_text(
        cls,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        return await asyncio.to_thread(
            cls.generate_text_sync,
            prompt,
            system_prompt,
            model,
        )
