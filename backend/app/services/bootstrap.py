from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.core.config import settings
from app.models.entities import AuditType, DocumentTemplate, Role, User
from app.services.catalog import audit_catalog


def seed_initial_data(db: Session) -> None:
    existing_admin = db.query(User).filter(User.email == settings.initial_admin_email).first()
    if not existing_admin:
        db.add(
            User(
                email=settings.initial_admin_email,
                full_name=settings.initial_admin_full_name,
                role=Role.admin,
                is_superuser=True,
                hashed_password=get_password_hash(settings.initial_admin_password),
            )
        )

    catalog = audit_catalog.load()
    for key, item in catalog.items():
        audit_type = AuditType(key)
        template = db.query(DocumentTemplate).filter(DocumentTemplate.audit_type == audit_type).first()
        if template:
            continue
        db.add(
            DocumentTemplate(
                audit_type=audit_type,
                title=item.get("title", key.replace("_", " ").title()),
                content_text=item.get("client_message", ""),
                required_documents=item.get("required_documents", []),
            )
        )
    db.commit()
