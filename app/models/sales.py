from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.people import User

# ─── Orders (материалы) ─────────────────────────────────────
ORDER_STATUSES = ("new", "confirmed", "assembling", "delivering", "done", "cancelled")

# ─── Leads / заявки ─────────────────────────────────────────
LEAD_SOURCES = ("site", "telegram", "phone")
LEAD_KINDS = ("materials", "master", "service", "turnkey", "calculator", "support", "other")
LEAD_STATUSES = ("new", "in_progress", "done", "spam")

# ─── CRM deal stages (mirror of the frontend kanban) ────────
DEAL_STAGES = ("new", "contact", "measure", "estimate", "contract", "inwork", "done", "lost")


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)

    customer_name: Mapped[str] = mapped_column(String(160))
    phone: Mapped[str] = mapped_column(String(32))
    address: Mapped[str] = mapped_column(Text, default="", server_default="")
    delivery: Mapped[str] = mapped_column(String(16), default="delivery", server_default="delivery")
    payment: Mapped[str] = mapped_column(String(16), default="kaspi", server_default="kaspi")
    comment: Mapped[str] = mapped_column(Text, default="", server_default="")

    status: Mapped[str] = mapped_column(String(16), default="new", server_default="new", index=True)
    subtotal: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    shipping: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    total: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    user: Mapped[User | None] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", lazy="selectin"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(240))
    price: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    unit: Mapped[str] = mapped_column(String(16), default="шт", server_default="шт")

    order: Mapped["Order"] = relationship(back_populates="items")


class Lead(Base, TimestampMixin):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(16), default="site", server_default="site", index=True)
    kind: Mapped[str] = mapped_column(String(20), default="other", server_default="other", index=True)
    name: Mapped[str] = mapped_column(String(160), default="", server_default="")
    phone: Mapped[str] = mapped_column(String(32), default="", server_default="")
    message: Mapped[str] = mapped_column(Text, default="", server_default="")
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(16), default="new", server_default="new", index=True)

    deal: Mapped["Deal | None"] = relationship(back_populates="lead", uselist=False)


class Deal(Base, TimestampMixin):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    client: Mapped[str] = mapped_column(String(200))
    phone: Mapped[str] = mapped_column(String(32), default="", server_default="")
    type: Mapped[str] = mapped_column(String(200), default="", server_default="")
    amount: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    stage: Mapped[str] = mapped_column(String(16), default="new", server_default="new", index=True)
    manager: Mapped[str] = mapped_column(String(120), default="", server_default="")
    source: Mapped[str] = mapped_column(String(16), default="site", server_default="site")
    note: Mapped[str] = mapped_column(Text, default="", server_default="")

    lead_id: Mapped[int | None] = mapped_column(ForeignKey("leads.id"), nullable=True, index=True)
    lead: Mapped["Lead | None"] = relationship(back_populates="deal")


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(40), default="info", server_default="info")
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text, default="", server_default="")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", index=True)
