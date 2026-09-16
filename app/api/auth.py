from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.core.deps import CurrentUser, DbDep
from app.core.security import REFRESH, create_token, decode_token, hash_password, verify_password
from app.models import User
from app.schemas.auth import (
    RefreshIn,
    RegisterIn,
    TokenOut,
    UserOut,
    UserUpdateIn,
)

router = APIRouter()


def _tokens(user: User) -> TokenOut:
    return TokenOut(
        access_token=create_token(user.id, "access"),
        refresh_token=create_token(user.id, "refresh"),
    )


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterIn, db: DbDep) -> TokenOut:
    exists = await db.scalar(select(User).where(User.email == data.email.lower()))
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    user = User(
        email=data.email.lower(),
        name=data.name,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role="customer",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _tokens(user)


@router.post("/login", response_model=TokenOut)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbDep
) -> TokenOut:
    """OAuth2 password flow — `username` field carries the email."""
    user = await db.scalar(select(User).where(User.email == form.username.lower()))
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account disabled")
    return _tokens(user)


@router.post("/refresh", response_model=TokenOut)
async def refresh(data: RefreshIn, db: DbDep) -> TokenOut:
    try:
        payload = decode_token(data.refresh_token)
        assert payload.get("type") == REFRESH
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token") from None
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
    return _tokens(user)


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser) -> User:
    return user


@router.patch("/me", response_model=UserOut)
async def update_me(data: UserUpdateIn, user: CurrentUser, db: DbDep) -> User:
    if data.name is not None:
        user.name = data.name
    if data.phone is not None:
        user.phone = data.phone
    await db.commit()
    await db.refresh(user)
    return user
