"""Write schemas for the admin management API (`/api/manage/*`)."""
from datetime import date

from pydantic import BaseModel, Field

# ─── Category ──────────────────────────────────────────────
class CategoryIn(BaseModel):
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=2000)
    image: str = Field(default="", max_length=1000)
    position: int = 0


class CategoryPatch(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    image: str | None = Field(default=None, max_length=1000)
    position: int | None = None


# ─── Brand ─────────────────────────────────────────────────
class BrandIn(BaseModel):
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    name: str = Field(min_length=1, max_length=160)


class BrandPatch(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    name: str | None = Field(default=None, min_length=1, max_length=160)


# ─── Product ───────────────────────────────────────────────
class SpecItem(BaseModel):
    label: str
    value: str


class ProductIn(BaseModel):
    slug: str = Field(min_length=1, max_length=160, pattern=r"^[a-z0-9-]+$")
    name: str = Field(min_length=1, max_length=240)
    category_id: int
    brand_id: int
    unit: str = Field(default="шт", max_length=16)
    price: int = Field(ge=0)
    old_price: int | None = Field(default=None, ge=0)
    stock: int = Field(default=0, ge=0)
    rating: float = Field(default=0, ge=0, le=5)
    review_count: int = Field(default=0, ge=0)
    image: str = Field(default="", max_length=1000)
    images: list[str] = Field(default_factory=list)
    badge: str = Field(default="", pattern=r"^(|hit|sale|new)$")
    short_description: str = Field(default="", max_length=500)
    description: str = Field(default="", max_length=5000)
    specs: list[SpecItem] = Field(default_factory=list)
    is_active: bool = True


class ProductPatch(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=160, pattern=r"^[a-z0-9-]+$")
    name: str | None = Field(default=None, min_length=1, max_length=240)
    category_id: int | None = None
    brand_id: int | None = None
    unit: str | None = Field(default=None, max_length=16)
    price: int | None = Field(default=None, ge=0)
    old_price: int | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    rating: float | None = Field(default=None, ge=0, le=5)
    review_count: int | None = Field(default=None, ge=0)
    image: str | None = Field(default=None, max_length=1000)
    images: list[str] | None = None
    badge: str | None = Field(default=None, pattern=r"^(|hit|sale|new)$")
    short_description: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    specs: list[SpecItem] | None = None
    is_active: bool | None = None


# ─── Master ────────────────────────────────────────────────
class MasterIn(BaseModel):
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    name: str = Field(min_length=1, max_length=160)
    specialty: list[str] = Field(default_factory=list)
    city: str = Field(default="Астана", max_length=80)
    district: str = Field(default="", max_length=80)
    rating: float = Field(default=0, ge=0, le=5)
    review_count: int = Field(default=0, ge=0)
    jobs: int = Field(default=0, ge=0)
    rate: int = Field(default=0, ge=0)
    verified: bool = False
    available: bool = True
    image: str = Field(default="", max_length=1000)
    bio: str = Field(default="", max_length=2000)
    portfolio: list[str] = Field(default_factory=list)
    location: dict = Field(default_factory=dict)


class MasterPatch(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    name: str | None = Field(default=None, min_length=1, max_length=160)
    specialty: list[str] | None = None
    city: str | None = Field(default=None, max_length=80)
    district: str | None = Field(default=None, max_length=80)
    rating: float | None = Field(default=None, ge=0, le=5)
    review_count: int | None = Field(default=None, ge=0)
    jobs: int | None = Field(default=None, ge=0)
    rate: int | None = Field(default=None, ge=0)
    verified: bool | None = None
    available: bool | None = None
    image: str | None = Field(default=None, max_length=1000)
    bio: str | None = Field(default=None, max_length=2000)
    portfolio: list[str] | None = None
    location: dict | None = None


# ─── Service ───────────────────────────────────────────────
class ServiceIn(BaseModel):
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    name: str = Field(min_length=1, max_length=200)
    price_from: int = Field(default=0, ge=0)
    duration: str = Field(default="", max_length=80)
    image: str = Field(default="", max_length=1000)
    description: str = Field(default="", max_length=3000)
    includes: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    gallery: list[str] = Field(default_factory=list)
    position: int = 0
    is_active: bool = True


class ServicePatch(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    name: str | None = Field(default=None, min_length=1, max_length=200)
    price_from: int | None = Field(default=None, ge=0)
    duration: str | None = Field(default=None, max_length=80)
    image: str | None = Field(default=None, max_length=1000)
    description: str | None = Field(default=None, max_length=3000)
    includes: list[str] | None = None
    steps: list[str] | None = None
    gallery: list[str] | None = None
    position: int | None = None
    is_active: bool | None = None


# ─── Vacancy ───────────────────────────────────────────────
class VacancyIn(BaseModel):
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    title: str = Field(min_length=1, max_length=200)
    city: str = Field(default="Астана", max_length=80)
    employment: str = Field(default="", max_length=80)
    salary_from: int = Field(default=0, ge=0)
    salary_to: int = Field(default=0, ge=0)
    short: str = Field(default="", max_length=500)
    responsibilities: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    is_open: bool = True


class VacancyPatch(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=120, pattern=r"^[a-z0-9-]+$")
    title: str | None = Field(default=None, min_length=1, max_length=200)
    city: str | None = Field(default=None, max_length=80)
    employment: str | None = Field(default=None, max_length=80)
    salary_from: int | None = Field(default=None, ge=0)
    salary_to: int | None = Field(default=None, ge=0)
    short: str | None = Field(default=None, max_length=500)
    responsibilities: list[str] | None = None
    requirements: list[str] | None = None
    conditions: list[str] | None = None
    is_open: bool | None = None


# ─── Article ───────────────────────────────────────────────
class ArticleIn(BaseModel):
    slug: str = Field(min_length=1, max_length=160, pattern=r"^[a-z0-9-]+$")
    title: str = Field(min_length=1, max_length=240)
    category: str = Field(default="", max_length=80)
    excerpt: str = Field(default="", max_length=600)
    image: str = Field(default="", max_length=1000)
    published_on: date
    read_min: int = Field(default=3, ge=1, le=90)
    body: list[str] = Field(default_factory=list)
    is_published: bool = True


class ArticlePatch(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=160, pattern=r"^[a-z0-9-]+$")
    title: str | None = Field(default=None, min_length=1, max_length=240)
    category: str | None = Field(default=None, max_length=80)
    excerpt: str | None = Field(default=None, max_length=600)
    image: str | None = Field(default=None, max_length=1000)
    published_on: date | None = None
    read_min: int | None = Field(default=None, ge=1, le=90)
    body: list[str] | None = None
    is_published: bool | None = None


# ─── FAQ ───────────────────────────────────────────────────
class FaqIn(BaseModel):
    section: str = Field(default="general", pattern=r"^(general|services)$")
    question: str = Field(min_length=1, max_length=500)
    answer: str = Field(min_length=1, max_length=3000)
    position: int = 0


class FaqPatch(BaseModel):
    section: str | None = Field(default=None, pattern=r"^(general|services)$")
    question: str | None = Field(default=None, min_length=1, max_length=500)
    answer: str | None = Field(default=None, min_length=1, max_length=3000)
    position: int | None = None
