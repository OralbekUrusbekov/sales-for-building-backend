from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

LeadKind = Literal["materials", "master", "service", "turnkey", "calculator", "support", "other"]
LeadSource = Literal["site", "telegram", "phone"]


class LeadCreate(BaseModel):
    kind: LeadKind = "other"
    source: LeadSource = "site"
    name: str = Field(default="", max_length=160)
    phone: str = Field(default="", max_length=32)
    message: str = Field(default="", max_length=4000)
    payload: dict = Field(default_factory=dict)


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str
    kind: str
    source: str
    name: str
    phone: str
    message: str
    payload: dict
    status: str
    created_at: datetime


class LeadStatusIn(BaseModel):
    status: Literal["new", "in_progress", "done", "spam"]
