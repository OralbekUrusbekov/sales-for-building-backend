from pydantic import BaseModel, ConfigDict


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: str
    image: str
    position: int
    product_count: int = 0


class BrandOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str


class ProductListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    unit: str
    price: int
    old_price: int | None
    stock: int
    rating: float
    review_count: int
    image: str
    badge: str
    short_description: str
    category: CategoryOut
    brand: BrandOut


class ProductOut(ProductListOut):
    images: list[str]
    description: str
    specs: list[dict]
