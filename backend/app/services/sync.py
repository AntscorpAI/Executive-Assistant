from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.integrations.local_audit_sync import local_audit_sync
from app.integrations.ms_graph import ms_graph_client
from app.models.entities import Audit, AuditType, User


@dataclass
class SyncResult:
    imported: int
    updated: int


class SyncService:
    async def sync_graph_calendar(self, db: Session, user_id: str | None = None) -> SyncResult:
        events = await ms_graph_client.get_calendar_events(user_id=user_id)
        imported = 0
        updated = 0
        for event in events:
            start_at = self._parse_dt(event.start_at)
            end_at = self._parse_dt(event.end_at)
            title = event.title or "Audit"
            audit = db.query(Audit).filter(Audit.title == title, Audit.start_at == start_at).first()
            if not audit:
                audit = Audit(
                    client_name=event.organizer or "Unknown client",
                    audit_type=AuditType.iso_9001,
                    title=title,
                    start_at=start_at,
                    end_at=end_at,
                    status="planned",
                    metadata_json={"source": "microsoft_graph"},
                )
                db.add(audit)
                imported += 1
            else:
                audit.end_at = end_at
                audit.metadata_json = {**audit.metadata_json, "source": "microsoft_graph"}
                updated += 1
        db.commit()
        return SyncResult(imported=imported, updated=updated)

    def import_local_file(self, db: Session, path: Path) -> SyncResult:
        imported = 0
        updated = 0
        if path.suffix.lower() == ".csv":
            records = local_audit_sync.import_csv(path)
        else:
            records = local_audit_sync.import_json(path)
        for record in records:
            start_at = self._parse_dt(record.start_at)
            end_at = self._parse_dt(record.end_at)
            audit_type = AuditType(record.audit_type)
            audit = db.query(Audit).filter(Audit.title == record.title, Audit.start_at == start_at).first()
            if not audit:
                audit = Audit(
                    client_name=record.client_name,
                    audit_type=audit_type,
                    title=record.title,
                    start_at=start_at,
                    end_at=end_at,
                    status="planned",
                    metadata_json={"source": "local_audit_sync", "auditor_email": record.auditor_email},
                )
                db.add(audit)
                imported += 1
            else:
                audit.end_at = end_at
                audit.metadata_json = {**audit.metadata_json, "source": "local_audit_sync", "auditor_email": record.auditor_email}
                updated += 1
        db.commit()
        return SyncResult(imported=imported, updated=updated)

    def _parse_dt(self, value: str) -> datetime:
        cleaned = value.replace("Z", "+00:00")
        return datetime.fromisoformat(cleaned)


sync_service = SyncService()
