from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.models.entities import User
from app.schemas.common import DocumentSearchRequest
from app.services.rag import rag_service

router = APIRouter()


@router.post("/search")
async def search_documents(payload: DocumentSearchRequest, db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> list[dict]:
    return await rag_service.search(payload.query, payload.top_k)


@router.post("/index")
async def index_documents(db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> dict[str, int]:
    indexed = await rag_service.index_templates(db)
    return {"indexed": indexed}
