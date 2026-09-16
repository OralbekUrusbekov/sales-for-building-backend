from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    image: Mapped[str] = mapped_column(Text, default="", server_default="")
    position: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Brand(Base, TimestampMixin):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))

    products: Mapped[list["Product"]] = relationship(back_populates="brand")


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(240))

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id"), index=True)

    unit: Mapped[str] = mapped_column(String(16), default="шт", server_default="шт")
    price: Mapped[int] = mapped_column(Integer)
    old_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stock: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    rating: Mapped[float] = mapped_column(Float, default=0, server_default="0")
    review_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    image: Mapped[str] = mapped_column(Text, default="", server_default="")
    images: Mapped[list] = mapped_column(JSONB, default=list)
    badge: Mapped[str] = mapped_column(String(16), default="", server_default="")
    short_description: Mapped[str] = mapped_column(Text, default="", server_default="")
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    specs: Mapped[list] = mapped_column(JSONB, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    category: Mapped["Category"] = relationship(back_populates="products", lazy="joined")
    brand: Mapped["Brand"] = relationship(back_populates="products", lazy="joined")
