from pathlib import Path
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import db_session, require_roles
from app.integrations.meeting_assistant import meeting_assistant
from app.integrations.ms_graph import ms_graph_client
from app.models.entities import Audit, DocumentTemplate, NotificationChannel, Role, User
from app.services.catalog import audit_catalog
from app.services.notifications import notification_service
from app.services.rag import rag_service
from app.services.sync import sync_service

router = APIRouter()


class LocalImportRequest(BaseModel):
    path: str


class OutboundMessageRequest(BaseModel):
    recipient: str
    body: str
    subject: str | None = None


class MeetingCommandRequest(BaseModel):
    transcript: str
    top_k: int = 3


@router.post("/microsoft-graph/sync")
async def sync_microsoft_graph(db: Session = Depends(db_session), user: User = Depends(require_roles(Role.manager, Role.admin))) -> dict:
    result = await sync_service.sync_graph_calendar(db)
    return {"imported": result.imported, "updated": result.updated}


@router.get("/microsoft-graph/preview")
async def preview_microsoft_graph(user: User = Depends(require_roles(Role.manager, Role.admin))) -> dict:
    events = await ms_graph_client.get_calendar_events()
    return {
        "count": len(events),
        "events": [
            {
                "title": item.title,
                "start_at": item.start_at,
                "end_at": item.end_at,
                "organizer": item.organizer,
                "location": item.location,
            }
            for item in events[:20]
        ],
    }


@router.post("/local-audit/import")
def import_local_audit(payload: LocalImportRequest, db: Session = Depends(db_session), user: User = Depends(require_roles(Role.manager, Role.admin))) -> dict:
    path = Path(payload.path).expanduser()
    if not path.exists():
        raise HTTPException(status_code=404, detail="Import file not found")
    result = sync_service.import_local_file(db, path)
    return {"imported": result.imported, "updated": result.updated}


@router.post("/whatsapp/test")
async def whatsapp_test(payload: OutboundMessageRequest, db: Session = Depends(db_session), user: User = Depends(require_roles(Role.manager, Role.admin))) -> dict:
    result = await notification_service.send(
        db,
        channel=NotificationChannel.whatsapp,
        recipient=payload.recipient,
        body=payload.body,
        subject=payload.subject,
    )
    return {"channel": result.channel.value, "recipient": result.recipient, "status": result.status, "external_id": result.external_id}


@router.post("/teams/test")
async def teams_test(payload: OutboundMessageRequest, db: Session = Depends(db_session), user: User = Depends(require_roles(Role.manager, Role.admin))) -> dict:
    result = await notification_service.send(
        db,
        channel=NotificationChannel.teams,
        recipient=payload.recipient,
        body=payload.body,
        subject=payload.subject,
    )
    return {"channel": result.channel.value, "recipient": result.recipient, "status": result.status, "external_id": result.external_id}


@router.post("/meetings/command")
async def meeting_command(payload: MeetingCommandRequest, db: Session = Depends(db_session), user: User = Depends(require_roles(Role.auditor, Role.manager, Role.admin))) -> dict:
    parsed = meeting_assistant.parse_command(payload.transcript)
    response: dict = {
        "intent": parsed.intent,
        "action_items": parsed.action_items,
        "opened_document": parsed.opened_document,
        "section_ref": parsed.section_ref,
        "audit_type": parsed.audit_type,
    }

    if parsed.intent == "show_schedule":
        now = datetime.now(timezone.utc)
        end = now + timedelta(days=7)
        audits = db.query(Audit).filter(Audit.start_at >= now, Audit.start_at <= end).order_by(Audit.start_at.asc()).all()
        response["schedule"] = [
            {
                "title": item.title,
                "client": item.client_name,
                "audit_type": item.audit_type.value,
                "start_at": item.start_at,
                "end_at": item.end_at,
                "expectations": item.expectations,
            }
            for item in audits
        ]

    if parsed.intent in {"open_checklist", "show_section"}:
        if parsed.audit_type:
            config = audit_catalog.get(parsed.audit_type)
            response["catalog_context"] = config

        query = payload.transcript
        rag_hits = await rag_service.search(query, top_k=payload.top_k)
        response["document_hits"] = rag_hits

        if parsed.section_ref:
            section_key = f"section {parsed.section_ref}".lower()
            section_extract = None
            for hit in rag_hits:
                text = (hit.get("content_text") or "")
                for line in text.splitlines():
                    if section_key in line.lower():
                        section_extract = line
                        break
                if section_extract:
                    break
            response["section_extract"] = section_extract

    return response
