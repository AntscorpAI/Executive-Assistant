from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Role(str, Enum):
    auditor = "auditor"
    manager = "manager"
    admin = "admin"


class TaskStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    blocked = "blocked"
    done = "done"


class NotificationChannel(str, Enum):
    whatsapp = "whatsapp"
    email = "email"
    teams = "teams"


class AuditType(str, Enum):
    iso_9001 = "iso_9001"
    iso_14001 = "iso_14001"
    iso_27001 = "iso_27001"
    iso_45001 = "iso_45001"
    iso_42001 = "iso_42001"


audit_auditors = Table(
    "audit_auditors",
    Base.metadata,
    Column("audit_id", ForeignKey("audits.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    role: Mapped[Role] = mapped_column(SAEnum(Role), default=Role.auditor, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    audits: Mapped[list[Audit]] = relationship(secondary=audit_auditors, back_populates="auditors")


class Audit(Base, TimestampMixin):
    __tablename__ = "audits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    client_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    client_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    audit_type: Mapped[AuditType] = mapped_column(SAEnum(AuditType), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="planned", nullable=False)
    expectations: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    auditors: Mapped[list[User]] = relationship(secondary=audit_auditors, back_populates="audits")
    tasks: Mapped[list[Task]] = relationship(back_populates="audit")


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(SAEnum(TaskStatus), default=TaskStatus.open, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reminder_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    owner_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assignee_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    related_audit_id: Mapped[str | None] = mapped_column(ForeignKey("audits.id", ondelete="SET NULL"), nullable=True)

    audit: Mapped[Audit | None] = relationship(back_populates="tasks")


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    channel: Mapped[NotificationChannel] = mapped_column(SAEnum(NotificationChannel), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    messages: Mapped[list[Message]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    direction: Mapped[str] = mapped_column(String(20), default="inbound", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="received", nullable=False)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class DocumentTemplate(Base, TimestampMixin):
    __tablename__ = "document_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    audit_type: Mapped[AuditType] = mapped_column(SAEnum(AuditType), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    required_documents: Mapped[list] = mapped_column(JSON, default=list, nullable=False)


class MemoryItem(Base, TimestampMixin):
    __tablename__ = "memory_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    scope: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    memory_key: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class ConflictEvent(Base, TimestampMixin):
    __tablename__ = "conflict_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    audit_id: Mapped[str] = mapped_column(ForeignKey("audits.id", ondelete="CASCADE"), nullable=False)
    conflict_type: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    details_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class NotificationLog(Base, TimestampMixin):
    __tablename__ = "notification_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    channel: Mapped[NotificationChannel] = mapped_column(SAEnum(NotificationChannel), nullable=False)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="queued", nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)


def import_models() -> None:
    _ = [User, Audit, Task, Conversation, Message, DocumentTemplate, MemoryItem, ConflictEvent, AuditLog, NotificationLog]
