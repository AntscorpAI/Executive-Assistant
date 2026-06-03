from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, require_roles
from app.models.entities import Audit, AuditType, Role, User
from app.schemas.common import AuditCreate, AuditRead, UserRead

router = APIRouter()


def to_user_read(user: User) -> UserRead:
    return UserRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone_number,
        role=user.role,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
    )


def to_audit_read(audit: Audit) -> AuditRead:
    return AuditRead(
        id=audit.id,
        client_name=audit.client_name,
        client_email=audit.client_email,
        audit_type=audit.audit_type,
        title=audit.title,
        location=audit.location,
        start_at=audit.start_at,
        end_at=audit.end_at,
        status=audit.status,
        expectations=audit.expectations,
        auditors=[to_user_read(item) for item in audit.auditors],
    )


@router.get("/", response_model=list[AuditRead])
def list_audits(db: Session = Depends(db_session), user: User = Depends(require_roles(Role.auditor, Role.manager, Role.admin))) -> list[AuditRead]:
    audits = db.query(Audit).order_by(Audit.start_at.asc()).all()
    return [to_audit_read(item) for item in audits]


@router.get("/upcoming", response_model=list[AuditRead])
def upcoming_audits(db: Session = Depends(db_session), user: User = Depends(require_roles(Role.auditor, Role.manager, Role.admin))) -> list[AuditRead]:
    audits = db.query(Audit).filter(Audit.status == "planned").order_by(Audit.start_at.asc()).limit(20).all()
    return [to_audit_read(item) for item in audits]


@router.post("/", response_model=AuditRead)
def create_audit(payload: AuditCreate, db: Session = Depends(db_session), user: User = Depends(require_roles(Role.manager, Role.admin))) -> AuditRead:
    audit = Audit(
        client_name=payload.client_name,
        client_email=payload.client_email,
        audit_type=payload.audit_type,
        title=payload.title,
        location=payload.location,
        start_at=payload.start_at,
        end_at=payload.end_at,
        expectations=payload.expectations,
    )
    if payload.auditor_ids:
        auditors = db.query(User).filter(User.id.in_(payload.auditor_ids)).all()
        audit.auditors = auditors
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return to_audit_read(audit)
