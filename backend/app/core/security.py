from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, role: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {"sub": subject, "role": role, "iss": settings.jwt_issuer, "aud": settings.jwt_audience, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, str]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"], audience=settings.jwt_audience)
        subject = payload.get("sub")
        role = payload.get("role")
        if not subject or not role:
            raise JWTError("Missing claims")
        return {"sub": subject, "role": role}
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
