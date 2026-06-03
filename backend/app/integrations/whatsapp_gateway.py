from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.core.config import settings


@dataclass
class WhatsAppMessage:
    recipient: str
    body: str
    subject: str | None = None


class WhatsAppGateway:
    async def send(self, message: WhatsAppMessage) -> str | None:
        if not settings.whatsapp_gateway_url:
            return None
        headers = {"Authorization": f"Bearer {settings.whatsapp_gateway_token}"} if settings.whatsapp_gateway_token else {}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{settings.whatsapp_gateway_url.rstrip('/')}/messages",
                json={"to": message.recipient, "message": message.body, "subject": message.subject},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return str(data.get("id") or data.get("messageId") or "") or None


whatsapp_gateway = WhatsAppGateway()
