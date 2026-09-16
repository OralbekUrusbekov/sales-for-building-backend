from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=9999)


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=160)
    phone: str = Field(min_length=5, max_length=32)
    address: str = Field(default="", max_length=500)
    delivery: Literal["delivery", "pickup"] = "delivery"
    payment: Literal["kaspi", "card", "cash"] = "kaspi"
    comment: str = Field(default="", max_length=2000)
    items: list[OrderItemIn] = Field(min_length=1)


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int | None
    name: str
    price: int
    quantity: int
    unit: str


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str
    customer_name: str
    phone: str
    address: str
    delivery: str
    payment: str
    comment: str
    status: str
    subtotal: int
    shipping: int
    total: int
    items: list[OrderItemOut]
    created_at: datetime


class OrderStatusIn(BaseModel):
    status: Literal["new", "confirmed", "assembling", "delivering", "done", "cancelled"]
