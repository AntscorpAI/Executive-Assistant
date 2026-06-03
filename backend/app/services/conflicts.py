from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.entities import Audit, ConflictEvent, User


class ConflictService:
    def detect_schedule_conflicts(self, db: Session) -> list[ConflictEvent]:
        audits = db.query(Audit).all()
        conflicts: list[ConflictEvent] = []
        by_user: dict[str, list[Audit]] = defaultdict(list)

        for audit in audits:
            for user in audit.auditors:
                by_user[user.id].append(audit)

        for user_id, user_audits in by_user.items():
            sorted_audits = sorted(user_audits, key=lambda item: item.start_at)
            for index in range(1, len(sorted_audits)):
                previous = sorted_audits[index - 1]
                current = sorted_audits[index]
                if current.start_at < previous.end_at:
                    conflicts.append(
                        ConflictEvent(
                            user_id=user_id,
                            audit_id=current.id,
                            conflict_type="schedule_overlap",
                            details=f"{current.title} overlaps with {previous.title}",
                            created_at=datetime.now(timezone.utc),
                            updated_at=datetime.now(timezone.utc),
                        )
                    )
        return conflicts

    def persist_conflicts(self, db: Session) -> list[ConflictEvent]:
        conflicts = self.detect_schedule_conflicts(db)
        for conflict in conflicts:
            db.add(conflict)
        db.commit()
        return conflicts


conflict_service = ConflictService()
