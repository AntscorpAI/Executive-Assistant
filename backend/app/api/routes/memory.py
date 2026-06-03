from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.models.entities import User
from app.services.memory import memory_service

router = APIRouter()


class MemoryCreate(BaseModel):
    scope: str
    key: str
    content: str


@router.get("/")
def list_memory(scope: str, query: str | None = None, db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> list[dict]:
    items = memory_service.recall(db, scope=scope, query=query, user_id=user.id)
    return [{"id": item.id, "scope": item.scope, "key": item.memory_key, "content": item.content, "metadata": item.metadata_json, "created_at": item.created_at} for item in items]


@router.post("/")
def create_memory(payload: MemoryCreate, db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> dict:
    item = memory_service.remember(db, scope=payload.scope, key=payload.key, content=payload.content, user_id=user.id)
    return {"id": item.id, "scope": item.scope, "key": item.memory_key, "content": item.content}
