from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import ACCESS, decode_token
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

DbDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str | None, Depends(oauth2_scheme)]

_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(db: DbDep, token: TokenDep) -> User:
    if not token:
        raise _CREDENTIALS_ERROR
    try:
        payload = decode_token(token)
        if payload.get("type") != ACCESS:
            raise _CREDENTIALS_ERROR
        user_id = int(payload["sub"])
    except Exception:  # any decode / claim failure is a 401
        raise _CREDENTIALS_ERROR from None

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise _CREDENTIALS_ERROR
    return user


async def get_optional_user(db: DbDep, token: TokenDep) -> User | None:
    if not token:
        return None
    try:
        return await get_current_user(db, token)
    except HTTPException:
        return None


def require_roles(*roles: str):
    async def _guard(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user

    return _guard


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
StaffUser = Annotated[User, Depends(require_roles("manager", "admin"))]
AdminUser = Annotated[User, Depends(require_roles("admin"))]
