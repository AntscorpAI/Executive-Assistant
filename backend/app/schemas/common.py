from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


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


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: str
    role: Role


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: str | None = None
    role: Role = Role.auditor


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserRead(UserBase):
    id: str
    is_active: bool
    is_superuser: bool
    created_at: datetime


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuditRead(BaseModel):
    id: str
    client_name: str
    client_email: str | None
    audit_type: AuditType
    title: str
    location: str | None
    start_at: datetime
    end_at: datetime
    status: str
    expectations: str | None = None
    auditors: list[UserRead] = []


class AuditCreate(BaseModel):
    client_name: str
    client_email: str | None = None
    audit_type: AuditType
    title: str
    location: str | None = None
    start_at: datetime
    end_at: datetime
    expectations: str | None = None
    auditor_ids: list[str] = []


class TaskRead(BaseModel):
    id: str
    title: str
    description: str | None
    status: TaskStatus
    priority: int
    due_at: datetime | None
    reminder_at: datetime | None
    owner_id: str | None
    assignee_id: str | None
    related_audit_id: str | None
    created_at: datetime


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: int = 3
    due_at: datetime | None = None
    reminder_at: datetime | None = None
    owner_id: str | None = None
    assignee_id: str | None = None
    related_audit_id: str | None = None


class DashboardSummary(BaseModel):
    total_users: int
    total_audits: int
    upcoming_today: int
    overdue_tasks: int
    pending_messages: int


class MessageCreate(BaseModel):
    channel: NotificationChannel
    recipient: str
    body: str
    subject: str | None = None


class DocumentSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class DocumentSearchHit(BaseModel):
    id: str
    title: str
    content_text: str
    score: float = 0.0
