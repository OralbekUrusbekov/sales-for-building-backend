from pydantic import BaseModel, ConfigDict


class MasterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    specialty: list[str]
    city: str
    district: str
    rating: float
    review_count: int
    jobs: int
    rate: int
    verified: bool
    available: bool
    image: str
    bio: str
    portfolio: list[str]
    location: dict
