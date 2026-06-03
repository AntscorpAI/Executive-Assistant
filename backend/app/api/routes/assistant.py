from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.models.entities import User
from app.services.assistant import assistant_service

router = APIRouter()


class AssistantCommand(BaseModel):
    text: str


@router.post("/command")
def command(payload: AssistantCommand, db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> dict:
    outcome = assistant_service.handle_text(db, user, payload.text)
    return {"intent": outcome.intent, "message": outcome.message, "payload": outcome.payload}
