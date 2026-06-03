from __future__ import annotations

from dataclasses import dataclass

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import NotificationChannel, NotificationLog


@dataclass
class NotificationResult:
    channel: NotificationChannel
    recipient: str
    status: str
    external_id: str | None = None


class NotificationService:
    async def send(self, db: Session, channel: NotificationChannel, recipient: str, body: str, subject: str | None = None) -> NotificationResult:
        payload = {"recipient": recipient, "body": body, "subject": subject}
        log = NotificationLog(channel=channel, recipient=recipient, payload_json=payload, status="queued")
        db.add(log)
        db.commit()
        db.refresh(log)

        external_id: str | None = None
        if channel == NotificationChannel.whatsapp:
            external_id = await self._send_whatsapp(recipient, body, subject)
        elif channel == NotificationChannel.email:
            external_id = await self._send_email(recipient, body, subject)
        elif channel == NotificationChannel.teams:
            external_id = await self._send_teams(recipient, body, subject)

        log.status = "sent" if external_id else "stored"
        log.external_id = external_id
        db.add(log)
        db.commit()
        return NotificationResult(channel=channel, recipient=recipient, status=log.status, external_id=external_id)

    async def _send_whatsapp(self, recipient: str, body: str, subject: str | None) -> str | None:
        if not settings.whatsapp_gateway_url:
            return None
        headers = {"Authorization": f"Bearer {settings.whatsapp_gateway_token}"} if settings.whatsapp_gateway_token else {}
        payload = {"to": recipient, "message": body, "subject": subject}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{settings.whatsapp_gateway_url.rstrip('/')}/messages", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        return str(data.get("id") or data.get("messageId") or "") or None

    async def _send_email(self, recipient: str, body: str, subject: str | None) -> str | None:
        return None

    async def _send_teams(self, recipient: str, body: str, subject: str | None) -> str | None:
        if not settings.ms_teams_webhook_url:
            return None
        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {"type": "TextBlock", "weight": "Bolder", "text": subject or "Sage Notification"},
                            {"type": "TextBlock", "text": body, "wrap": True},
                            {"type": "TextBlock", "spacing": "Small", "isSubtle": True, "text": f"Recipient: {recipient}"},
                        ],
                    },
                }
            ],
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(settings.ms_teams_webhook_url, json=payload)
            response.raise_for_status()
        return "teams-webhook"

        return None


notification_service = NotificationService()
