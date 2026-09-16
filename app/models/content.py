from datetime import date

from sqlalchemy import Boolean, Date, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Service(Base, TimestampMixin):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    price_from: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    duration: Mapped[str] = mapped_column(String(80), default="", server_default="")
    image: Mapped[str] = mapped_column(Text, default="", server_default="")
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    includes: Mapped[list] = mapped_column(JSONB, default=list)
    steps: Mapped[list] = mapped_column(JSONB, default=list)
    gallery: Mapped[list] = mapped_column(JSONB, default=list)
    position: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")


class Vacancy(Base, TimestampMixin):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    city: Mapped[str] = mapped_column(String(80), default="Астана", server_default="Астана")
    employment: Mapped[str] = mapped_column(String(80), default="", server_default="")
    salary_from: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    salary_to: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    short: Mapped[str] = mapped_column(Text, default="", server_default="")
    responsibilities: Mapped[list] = mapped_column(JSONB, default=list)
    requirements: Mapped[list] = mapped_column(JSONB, default=list)
    conditions: Mapped[list] = mapped_column(JSONB, default=list)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")


class Article(Base, TimestampMixin):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(240))
    category: Mapped[str] = mapped_column(String(80), default="", server_default="")
    excerpt: Mapped[str] = mapped_column(Text, default="", server_default="")
    image: Mapped[str] = mapped_column(Text, default="", server_default="")
    published_on: Mapped[date] = mapped_column(Date)
    read_min: Mapped[int] = mapped_column(Integer, default=3, server_default="3")
    body: Mapped[list] = mapped_column(JSONB, default=list)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")


class FaqItem(Base, TimestampMixin):
    __tablename__ = "faq_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    section: Mapped[str] = mapped_column(String(40), default="general", server_default="general", index=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
