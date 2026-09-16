from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

ROLE_CUSTOMER = "customer"
ROLE_MANAGER = "manager"
ROLE_ADMIN = "admin"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(32), default="", server_default="")
    name: Mapped[str] = mapped_column(String(160), default="", server_default="")
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), default=ROLE_CUSTOMER, server_default=ROLE_CUSTOMER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class Master(Base, TimestampMixin):
    __tablename__ = "masters"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    specialty: Mapped[list] = mapped_column(JSONB, default=list)
    city: Mapped[str] = mapped_column(String(80), default="Астана", server_default="Астана")
    district: Mapped[str] = mapped_column(String(80), default="", server_default="")
    rating: Mapped[float] = mapped_column(Float, default=0, server_default="0")
    review_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    jobs: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    rate: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    available: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    image: Mapped[str] = mapped_column(Text, default="", server_default="")
    bio: Mapped[str] = mapped_column(Text, default="", server_default="")
    portfolio: Mapped[list] = mapped_column(JSONB, default=list)
    location: Mapped[dict] = mapped_column(JSONB, default=dict)
