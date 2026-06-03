from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.entities import Audit, Task, User
from app.services.catalog import audit_catalog
from app.services.memory import memory_service


@dataclass
class AssistantOutcome:
    intent: str
    message: str
    payload: dict


class AssistantService:
    def handle_text(self, db: Session, user: User, text: str) -> AssistantOutcome:
        lowered = text.lower().strip()

        if lowered.startswith("add task"):
            task = Task(title=text, owner_id=user.id, assignee_id=user.id)
            db.add(task)
            db.commit()
            db.refresh(task)
            memory_service.remember(db, scope="tasks", key=task.id, content=text, user_id=user.id, metadata={"task_id": task.id})
            return AssistantOutcome(intent="task_created", message="Task added.", payload={"task_id": task.id})

        if "schedule" in lowered or "audit" in lowered:
            audits = db.query(Audit).order_by(Audit.start_at.asc()).limit(10).all()
            lines = [f"{item.start_at:%Y-%m-%d %H:%M} {item.title} - {item.client_name}" for item in audits]
            return AssistantOutcome(intent="schedule_lookup", message="Upcoming audits loaded.", payload={"audits": lines})

        for audit_type in audit_catalog.load().keys():
            if audit_type.replace("iso_", "iso ") in lowered or audit_type in lowered:
                checklist = audit_catalog.get(audit_type)
                return AssistantOutcome(
                    intent="document_lookup",
                    message=checklist.get("client_message", "Checklist loaded."),
                    payload={"audit_type": audit_type, "checklist": checklist},
                )

        memory_service.remember(db, scope="conversations", key=text[:120], content=text, user_id=user.id)
        return AssistantOutcome(intent="general_note", message="Saved to memory for follow-up.", payload={})


assistant_service = AssistantService()
