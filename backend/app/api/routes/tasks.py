from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user, require_roles
from app.models.entities import Role, Task, TaskStatus, User
from app.schemas.common import TaskCreate, TaskRead

router = APIRouter()


def to_task_read(task: Task) -> TaskRead:
    return TaskRead(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_at=task.due_at,
        reminder_at=task.reminder_at,
        owner_id=task.owner_id,
        assignee_id=task.assignee_id,
        related_audit_id=task.related_audit_id,
        created_at=task.created_at,
    )


@router.get("/", response_model=list[TaskRead])
def list_tasks(db: Session = Depends(db_session), user: User = Depends(require_roles(Role.auditor, Role.manager, Role.admin))) -> list[TaskRead]:
    tasks = db.query(Task).order_by(Task.created_at.desc()).all()
    return [to_task_read(task) for task in tasks]


@router.post("/", response_model=TaskRead)
def create_task(payload: TaskCreate, db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> TaskRead:
    task = Task(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_at=payload.due_at,
        reminder_at=payload.reminder_at,
        owner_id=payload.owner_id or user.id,
        assignee_id=payload.assignee_id,
        related_audit_id=payload.related_audit_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return to_task_read(task)


@router.patch("/{task_id}/status", response_model=TaskRead)
def update_task_status(task_id: str, status_payload: dict[str, str], db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> TaskRead:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    task.status = TaskStatus(status_payload["status"])
    db.add(task)
    db.commit()
    db.refresh(task)
    return to_task_read(task)
