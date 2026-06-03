import httpx
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    payload = {"status": "ok", "service": "sage-ai", "llm": {"status": "unknown", "url": settings.active_ollama_base_url, "chat_model": settings.active_ollama_chat_model}}
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get(f"{settings.active_ollama_base_url.rstrip('/')}/api/tags")
            response.raise_for_status()
            models = [item.get("name", "") for item in response.json().get("models", []) if item.get("name")]
            payload["llm"] = {
                "status": "ok",
                "url": settings.active_ollama_base_url,
                "chat_model": settings.active_ollama_chat_model,
                "available_models": models,
                "chat_model_pulled": settings.active_ollama_chat_model in models,
            }
    except Exception as exc:
        payload["llm"] = {
            "status": "unreachable",
            "url": settings.active_ollama_base_url,
            "chat_model": settings.active_ollama_chat_model,
            "error": str(exc),
        }
    return payload
