from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Stage = Literal["new", "contact", "measure", "estimate", "contract", "inwork", "done", "lost"]
Source = Literal["site", "telegram", "phone"]


class StageOut(BaseModel):
    key: str
    label: str
    tone: str


class DealOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    client: str
    phone: str
    type: str
    amount: int
    stage: str
    manager: str
    source: str
    note: str
    lead_id: int | None
    created_at: datetime


class DealCreate(BaseModel):
    client: str = Field(min_length=2, max_length=200)
    phone: str = Field(default="", max_length=32)
    type: str = Field(default="", max_length=200)
    amount: int = Field(default=0, ge=0)
    stage: Stage = "new"
    manager: str = Field(default="", max_length=120)
    source: Source = "site"
    note: str = Field(default="", max_length=2000)


class DealUpdate(BaseModel):
    client: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=32)
    type: str | None = Field(default=None, max_length=200)
    amount: int | None = Field(default=None, ge=0)
    stage: Stage | None = None
    manager: str | None = Field(default=None, max_length=120)
    note: str | None = Field(default=None, max_length=2000)


class BoardColumn(BaseModel):
    stage: StageOut
    count: int
    total: int
    deals: list[DealOut]


class CrmBoard(BaseModel):
    columns: list[BoardColumn]
    managers: list[str]
    open_total: int
    won_total: int
