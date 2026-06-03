from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.entities import AuditLog, Role, User
from app.schemas.common import LoginRequest, Token, UserCreate, UserRead

router = APIRouter()


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_session)) -> Token:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.email, role=user.role.value, expires_delta=timedelta(minutes=settings.access_token_expire_minutes))
    db.add(AuditLog(actor_id=user.id, action="login", entity_type="user", entity_id=user.id, details_json={"email": user.email}))
    db.commit()
    return Token(access_token=token)


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)) -> UserRead:
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


@router.post("/bootstrap", response_model=UserRead)
def bootstrap_user(payload: UserCreate, db: Session = Depends(db_session)) -> UserRead:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    user = User(email=payload.email, full_name=payload.full_name, phone_number=payload.phone_number, role=payload.role, hashed_password=get_password_hash(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRead(id=user.id, email=user.email, full_name=user.full_name, phone_number=user.phone_number, role=user.role, is_active=user.is_active, is_superuser=user.is_superuser, created_at=user.created_at)
