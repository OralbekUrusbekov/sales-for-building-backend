from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin

# target_type: product | master | service
STATUS_PENDING = "pending"
STATUS_PUBLISHED = "published"
STATUS_REJECTED = "rejected"


class Review(Base, TimestampMixin):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    target_type: Mapped[str] = mapped_column(String(16), index=True)
    target_id: Mapped[str] = mapped_column(String(64), index=True)
    author_name: Mapped[str] = mapped_column(String(160))
    avatar: Mapped[str] = mapped_column(Text, default="", server_default="")
    rating: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    photos: Mapped[list] = mapped_column(JSONB, default=list)
    status: Mapped[str] = mapped_column(
        String(16), default=STATUS_PENDING, server_default=STATUS_PENDING, index=True
    )
