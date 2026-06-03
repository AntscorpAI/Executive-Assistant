from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.core.config import settings


@dataclass
class LLMResult:
    text: str
    provider: str


class LLMService:
    async def chat(self, messages: list[dict[str, str]], temperature: float = 0.2) -> LLMResult:
        if settings.default_llm_provider.lower() == "claude" and settings.anthropic_api_key:
            return await self._chat_claude(messages, temperature)
        return await self._chat_ollama(messages, temperature)

    async def _chat_ollama(self, messages: list[dict[str, str]], temperature: float) -> LLMResult:
        payload = {"model": settings.active_ollama_chat_model, "messages": messages, "stream": False, "options": {"temperature": temperature}}
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{settings.active_ollama_base_url.rstrip('/')}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
        return LLMResult(text=data["message"]["content"], provider="ollama")

    async def _chat_claude(self, messages: list[dict[str, str]], temperature: float) -> LLMResult:
        headers = {
            "x-api-key": settings.anthropic_api_key or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": "claude-3-5-sonnet-latest",
            "max_tokens": 1024,
            "temperature": temperature,
            "messages": messages,
        }
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        text = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
        return LLMResult(text=text, provider="claude")


llm_service = LLMService()
