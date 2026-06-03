from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import httpx

from app.core.config import settings


@dataclass
class CalendarEvent:
    title: str
    start_at: str
    end_at: str
    organizer: str | None = None
    attendee_emails: list[str] | None = None
    location: str | None = None
    body_preview: str | None = None


class MicrosoftGraphClient:
    async def get_access_token(self) -> str | None:
        if not all([settings.ms_graph_tenant_id, settings.ms_graph_client_id, settings.ms_graph_client_secret]):
            return None
        payload = {
            "client_id": settings.ms_graph_client_id,
            "client_secret": settings.ms_graph_client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"https://login.microsoftonline.com/{settings.ms_graph_tenant_id}/oauth2/v2.0/token", data=payload)
            response.raise_for_status()
            return response.json().get("access_token")

    async def get_calendar_events(self, user_id: str | None = None) -> list[CalendarEvent]:
        token = await self.get_access_token()
        if not token:
            return []
        target_user = user_id or settings.ms_graph_user_id
        if not target_user:
            return []
        headers = {"Authorization": f"Bearer {token}"}
        now = datetime.now(timezone.utc)
        start_at = now.isoformat().replace("+00:00", "Z")
        end_at = (now + timedelta(days=30)).isoformat().replace("+00:00", "Z")
        params = {
            "startDateTime": start_at,
            "endDateTime": end_at,
            "$select": "subject,start,end,organizer,attendees,location,bodyPreview",
            "$orderby": "start/dateTime",
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"https://graph.microsoft.com/v1.0/users/{target_user}/calendarView", headers=headers, params=params)
            response.raise_for_status()
            data = response.json().get("value", [])
        events: list[CalendarEvent] = []
        for item in data:
            attendees = [a.get("emailAddress", {}).get("address", "") for a in item.get("attendees", []) if a.get("emailAddress", {}).get("address")]
            events.append(
                CalendarEvent(
                    title=item.get("subject", "Audit"),
                    start_at=item.get("start", {}).get("dateTime", ""),
                    end_at=item.get("end", {}).get("dateTime", ""),
                    organizer=item.get("organizer", {}).get("emailAddress", {}).get("address"),
                    attendee_emails=attendees,
                    location=item.get("location", {}).get("displayName"),
                    body_preview=item.get("bodyPreview", ""),
                )
            )
        return events


ms_graph_client = MicrosoftGraphClient()
