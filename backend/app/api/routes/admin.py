from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import db_session, require_roles
from app.models.entities import Audit, NotificationLog, Role, Task, User
from app.schemas.common import DashboardSummary

router = APIRouter()


@router.get("/overview", response_model=DashboardSummary)
def overview(db: Session = Depends(db_session), user: User = Depends(require_roles(Role.manager, Role.admin))) -> DashboardSummary:
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_audits = db.query(func.count(Audit.id)).scalar() or 0
    upcoming_today = db.query(func.count(Audit.id)).filter(Audit.status == "planned").scalar() or 0
    overdue_tasks = db.query(func.count(Task.id)).filter(Task.status != "done").scalar() or 0
    pending_messages = db.query(func.count(NotificationLog.id)).filter(NotificationLog.status != "sent").scalar() or 0
    return DashboardSummary(
        total_users=total_users,
        total_audits=total_audits,
        upcoming_today=upcoming_today,
        overdue_tasks=overdue_tasks,
        pending_messages=pending_messages,
    )


@router.get("/health")
def admin_health() -> dict[str, str]:
    return {"status": "healthy"}
