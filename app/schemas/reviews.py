from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TargetType = Literal["product", "master", "service"]


class ReviewIn(BaseModel):
    target_type: TargetType
    target_id: str = Field(max_length=64)
    author_name: str = Field(min_length=2, max_length=160)
    rating: int = Field(ge=1, le=5)
    text: str = Field(min_length=3, max_length=4000)
    photos: list[str] = Field(default_factory=list)


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    target_type: str
    target_id: str
    author_name: str
    avatar: str
    rating: int
    text: str
    photos: list[str]
    status: str
    created_at: datetime


class RatingBucket(BaseModel):
    star: int
    count: int
    pct: int


class ReviewStats(BaseModel):
    total: int
    avg: float
    dist: list[RatingBucket]
