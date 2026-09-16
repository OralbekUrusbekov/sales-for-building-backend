from typing import Literal

from pydantic import BaseModel, Field

RoomKey = Literal["bathroom", "kitchen", "room", "corridor", "apartment"]
WorkKey = Literal[
    "demolition", "plaster", "electric", "tile", "plumbing", "paint", "floor", "ceiling"
]


class CalcIn(BaseModel):
    room: RoomKey
    area: float = Field(gt=0, le=1000, description="площадь помещения, м²")
    works: list[WorkKey] = Field(min_length=1)
    finish: Literal["econom", "standard", "premium"] = "standard"
    # optional contact — when present a lead is created
    name: str = Field(default="", max_length=160)
    phone: str = Field(default="", max_length=32)


class CalcLine(BaseModel):
    key: str
    label: str
    amount: int


class CalcOut(BaseModel):
    area: float
    room_label: str
    works_cost: int
    materials_cost: int
    equipment_cost: int
    total_min: int
    total_max: int
    breakdown: list[CalcLine]
    lead_number: str | None = None
