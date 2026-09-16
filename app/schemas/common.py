from math import ceil
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Message(BaseModel):
    detail: str


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int

    @classmethod
    def build(cls, items: list[T], total: int, page: int, per_page: int) -> "Page[T]":
        return cls(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=max(1, ceil(total / per_page)) if per_page else 1,
        )
