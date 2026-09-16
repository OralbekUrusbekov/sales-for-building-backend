from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS = "access"
REFRESH = "refresh"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_token(subject: str | int, kind: str = ACCESS, expires: timedelta | None = None) -> str:
    now = datetime.now(timezone.utc)
    if expires is None:
        expires = (
            timedelta(minutes=settings.access_token_expire_minutes)
            if kind == ACCESS
            else timedelta(days=settings.refresh_token_expire_days)
        )
    payload: dict[str, Any] = {"sub": str(subject), "type": kind, "iat": now, "exp": now + expires}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
