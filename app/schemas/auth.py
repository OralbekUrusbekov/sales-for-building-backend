from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    name: str = Field(default="", max_length=160)
    phone: str = Field(default="", max_length=32)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    phone: str
    role: str
    is_active: bool
    created_at: datetime


class UserUpdateIn(BaseModel):
    name: str | None = Field(default=None, max_length=160)
    phone: str | None = Field(default=None, max_length=32)
