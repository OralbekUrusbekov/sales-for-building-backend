from datetime import date

from pydantic import BaseModel, ConfigDict


class ServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    price_from: int
    duration: str
    image: str
    description: str
    includes: list[str]
    steps: list[str]
    gallery: list[str]


class VacancyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    city: str
    employment: str
    salary_from: int
    salary_to: int
    short: str
    responsibilities: list[str]
    requirements: list[str]
    conditions: list[str]
    is_open: bool


class ArticleListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    category: str
    excerpt: str
    image: str
    published_on: date
    read_min: int


class ArticleOut(ArticleListOut):
    body: list[str]


class FaqOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    section: str
    question: str
    answer: str
    position: int
