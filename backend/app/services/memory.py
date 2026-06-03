from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.entities import MemoryItem


class MemoryService:
    def remember(self, db: Session, scope: str, key: str, content: str, user_id: str | None = None, metadata: dict | None = None) -> MemoryItem:
        item = MemoryItem(scope=scope, memory_key=key, content=content, user_id=user_id, metadata_json=metadata or {})
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def recall(self, db: Session, scope: str, query: str | None = None, user_id: str | None = None, limit: int = 20) -> list[MemoryItem]:
        statement = db.query(MemoryItem).filter(MemoryItem.scope == scope)
        if user_id:
            statement = statement.filter(MemoryItem.user_id == user_id)
        if query:
            like = f"%{query}%"
            statement = statement.filter((MemoryItem.memory_key.ilike(like)) | (MemoryItem.content.ilike(like)))
        return statement.order_by(MemoryItem.created_at.desc()).limit(limit).all()


memory_service = MemoryService()
