from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.models.entities import Conversation, Message, NotificationChannel, User
from app.schemas.common import MessageCreate

router = APIRouter()


@router.get("/conversations")
def list_conversations(db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> list[dict]:
    conversations = db.query(Conversation).order_by(Conversation.created_at.desc()).all()
    return [
        {
            "id": item.id,
            "channel": item.channel.value,
            "subject": item.subject,
            "external_id": item.external_id,
            "message_count": len(item.messages),
            "created_at": item.created_at,
        }
        for item in conversations
    ]


@router.post("/send")
def create_message(payload: MessageCreate, db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> dict:
    conversation = db.query(Conversation).filter(Conversation.channel == payload.channel, Conversation.external_id == payload.recipient).first()
    if not conversation:
        conversation = Conversation(channel=payload.channel, external_id=payload.recipient, subject=payload.subject, user_id=user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    message = Message(conversation_id=conversation.id, sender=user.email, body=payload.body, direction="outbound", status="queued")
    db.add(message)
    db.commit()
    return {"conversation_id": conversation.id, "message_id": message.id, "status": "queued"}
