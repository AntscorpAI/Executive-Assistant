from __future__ import annotations

from datetime import datetime, time, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.entities import Audit, NotificationChannel, Role, Task, User
from app.services.notifications import notification_service
from app.services.reminders import reminder_service


class SageScheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler(timezone=timezone.utc)

    def start(self) -> None:
        if self.scheduler.running:
            return
        self.scheduler.add_job(self.daily_briefing, "cron", hour=8, minute=0, id="daily_briefing", replace_existing=True)
        self.scheduler.add_job(self.friday_digest, "cron", day_of_week="fri", hour=18, minute=0, id="friday_digest", replace_existing=True)
        self.scheduler.add_job(self.overdue_follow_up, "interval", hours=4, id="overdue_follow_up", replace_existing=True)
        self.scheduler.start()

    async def daily_briefing(self) -> None:
        db = SessionLocal()
        try:
            today = datetime.now(timezone.utc).date()
            audits = db.query(Audit).filter(func.date(Audit.start_at) == today).all()
            auditors = db.query(User).filter(User.role.in_([Role.auditor, Role.manager])).all()
            for user in auditors:
                body = reminder_service.build_auditor_digest(audits, "Today\'s audit schedule")
                if user.phone_number:
                    await notification_service.send(db, NotificationChannel.whatsapp, user.phone_number, body, "Morning audit briefing")
            for audit in audits:
                if audit.client_email:
                    client_body = reminder_service.build_client_checklist(audit)
                    await notification_service.send(db, NotificationChannel.email, audit.client_email, client_body, f"Documentation reminder for {audit.title}")
        finally:
            db.close()

    async def friday_digest(self) -> None:
        db = SessionLocal()
        try:
            audits = db.query(Audit).filter(Audit.status == "planned").order_by(Audit.start_at.asc()).all()
            auditors = db.query(User).filter(User.role.in_([Role.auditor, Role.manager])).all()
            for user in auditors:
                body = reminder_service.build_auditor_digest(audits, "Upcoming audits next week")
                if user.phone_number:
                    await notification_service.send(db, NotificationChannel.whatsapp, user.phone_number, body, "Friday audit digest")
            for audit in audits:
                if audit.client_email:
                    client_body = reminder_service.build_client_checklist(audit)
                    await notification_service.send(db, NotificationChannel.email, audit.client_email, client_body, f"Prepare documents for {audit.title}")
        finally:
            db.close()

    async def overdue_follow_up(self) -> None:
        db = SessionLocal()
        try:
            overdue_tasks = db.query(Task).filter(Task.status != "done").all()
            owners = {item.owner_id for item in overdue_tasks if item.owner_id}
            for owner_id in owners:
                user = db.query(User).filter(User.id == owner_id).first()
                if user and user.phone_number:
                    body = f"You have {len([task for task in overdue_tasks if task.owner_id == owner_id])} open or overdue tasks in Sage AI."
                    await notification_service.send(db, NotificationChannel.whatsapp, user.phone_number, body, "Task follow-up")
        finally:
            db.close()

    def _render_briefing(self, heading: str, audits: list[Audit]) -> str:
        lines = [f"{heading} in Sage AI:"]
        for audit in audits[:10]:
            lines.append(f"- {audit.start_at:%Y-%m-%d %H:%M} {audit.title} for {audit.client_name}")
        return "\n".join(lines)


scheduler_service = SageScheduler()
