from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, or_, select

from app.core.deps import DbDep
from app.models import Brand, Category, Product
from app.schemas.catalog import BrandOut, CategoryOut, ProductListOut, ProductOut
from app.schemas.common import Page

router = APIRouter()

SortKey = Literal["popular", "price_asc", "price_desc", "rating", "new"]


@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: DbDep) -> list[CategoryOut]:
    counts = dict(
        (
            await db.execute(
                select(Product.category_id, func.count())
                .where(Product.is_active.is_(True))
                .group_by(Product.category_id)
            )
        ).all()
    )
    rows = (await db.scalars(select(Category).order_by(Category.position, Category.id))).all()
    return [
        CategoryOut.model_validate(c, from_attributes=True).model_copy(
            update={"product_count": counts.get(c.id, 0)}
        )
        for c in rows
    ]


@router.get("/categories/{slug}", response_model=CategoryOut)
async def get_category(slug: str, db: DbDep) -> CategoryOut:
    category = await db.scalar(select(Category).where(Category.slug == slug))
    if not category:
        raise HTTPException(404, "Category not found")
    count = await db.scalar(
        select(func.count()).select_from(Product).where(Product.category_id == category.id)
    )
    out = CategoryOut.model_validate(category, from_attributes=True)
    return out.model_copy(update={"product_count": count or 0})


@router.get("/brands", response_model=list[BrandOut])
async def list_brands(db: DbDep) -> list[Brand]:
    return list(await db.scalars(select(Brand).order_by(Brand.name)))


@router.get("/products", response_model=Page[ProductListOut])
async def list_products(
    db: DbDep,
    q: str | None = None,
    category: str | None = Query(default=None, description="category slug"),
    brand: list[str] | None = Query(default=None, description="brand slug(s)"),
    price_min: int | None = Query(default=None, ge=0),
    price_max: int | None = Query(default=None, ge=0),
    badge: Literal["hit", "sale", "new"] | None = None,
    in_stock: bool | None = None,
    sort: SortKey = "popular",
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=24, ge=1, le=500),
) -> Page[ProductListOut]:
    stmt = select(Product).where(Product.is_active.is_(True))

    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Product.name.ilike(like), Product.short_description.ilike(like)))
    if category:
        stmt = stmt.join(Category).where(Category.slug == category)
    if brand:
        stmt = stmt.join(Brand).where(Brand.slug.in_(brand))
    if price_min is not None:
        stmt = stmt.where(Product.price >= price_min)
    if price_max is not None:
        stmt = stmt.where(Product.price <= price_max)
    if badge:
        stmt = stmt.where(Product.badge == badge)
    if in_stock:
        stmt = stmt.where(Product.stock > 0)

    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    order = {
        "popular": (Product.review_count.desc(), Product.rating.desc()),
        "price_asc": (Product.price.asc(),),
        "price_desc": (Product.price.desc(),),
        "rating": (Product.rating.desc(), Product.review_count.desc()),
        "new": (Product.created_at.desc(), Product.id.desc()),
    }[sort]
    stmt = stmt.order_by(*order).offset((page - 1) * per_page).limit(per_page)

    rows = list(await db.scalars(stmt))
    return Page.build(
        [ProductListOut.model_validate(r, from_attributes=True) for r in rows],
        total,
        page,
        per_page,
    )


@router.get("/products/{key}", response_model=ProductOut)
async def get_product(key: str, db: DbDep) -> Product:
    stmt = select(Product).where(Product.slug == key)
    if key.isdigit():
        stmt = select(Product).where(or_(Product.slug == key, Product.id == int(key)))
    product = await db.scalar(stmt)
    if not product:
        raise HTTPException(404, "Product not found")
    return product
