"""Admin management API — staff-only CRUD for every content entity.

Mounted at ``/api/manage``. All routes require a manager/admin token.
List endpoints here return *all* rows (including inactive/unpublished) unlike
the public routers.
"""
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.core.deps import DbDep, StaffUser
from app.models import (
    Article,
    Brand,
    Category,
    FaqItem,
    Master,
    Product,
    Service,
    Vacancy,
)
from app.models.base import Base
from app.schemas.catalog import BrandOut, CategoryOut, ProductListOut, ProductOut
from app.schemas.common import Page
from app.schemas.content import ArticleOut, FaqOut, ServiceOut, VacancyOut
from app.schemas.manage import (
    ArticleIn,
    ArticlePatch,
    BrandIn,
    BrandPatch,
    CategoryIn,
    CategoryPatch,
    FaqIn,
    FaqPatch,
    MasterIn,
    MasterPatch,
    ProductIn,
    ProductPatch,
    ServiceIn,
    ServicePatch,
    VacancyIn,
    VacancyPatch,
)
from app.schemas.masters import MasterOut

router = APIRouter()


# ─── helpers ───────────────────────────────────────────────
async def _get_or_404(db, model: type[Base], obj_id: int):
    obj = await db.get(model, obj_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"{model.__name__} not found")
    return obj


async def _slug_free(db, model: type[Base], slug: str, exclude_id: int | None = None) -> None:
    stmt = select(model.id).where(model.slug == slug)  # type: ignore[attr-defined]
    if exclude_id is not None:
        stmt = stmt.where(model.id != exclude_id)  # type: ignore[attr-defined]
    if await db.scalar(stmt):
        raise HTTPException(status.HTTP_409_CONFLICT, f"slug '{slug}' already exists")


def _apply(obj, data: BaseModel) -> None:
    for key, value in data.model_dump(exclude_unset=True).items():
        if key == "specs" and value is not None:
            value = [s if isinstance(s, dict) else s.model_dump() for s in value]
        setattr(obj, key, value)


async def _delete(db, obj) -> None:
    try:
        await db.delete(obj)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Запись используется другими данными и не может быть удалена"
        ) from None


async def _paginated(db, stmt, schema, page: int, per_page: int) -> Page:
    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = list(await db.scalars(stmt.offset((page - 1) * per_page).limit(per_page)))
    return Page.build(
        [schema.model_validate(r, from_attributes=True) for r in rows], total, page, per_page
    )


# ─── Categories ────────────────────────────────────────────
@router.get("/categories", response_model=list[CategoryOut])
async def categories_list(db: DbDep, _: StaffUser):
    rows = await db.scalars(select(Category).order_by(Category.position, Category.id))
    return list(rows)


@router.post("/categories", response_model=CategoryOut, status_code=201)
async def categories_create(data: CategoryIn, db: DbDep, _: StaffUser):
    await _slug_free(db, Category, data.slug)
    obj = Category(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.patch("/categories/{obj_id}", response_model=CategoryOut)
async def categories_update(obj_id: int, data: CategoryPatch, db: DbDep, _: StaffUser):
    obj = await _get_or_404(db, Category, obj_id)
    if data.slug and data.slug != obj.slug:
        await _slug_free(db, Category, data.slug, obj_id)
    _apply(obj, data)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/categories/{obj_id}", status_code=204)
async def categories_delete(obj_id: int, db: DbDep, _: StaffUser):
    await _delete(db, await _get_or_404(db, Category, obj_id))


# ─── Brands ────────────────────────────────────────────────
@router.get("/brands", response_model=list[BrandOut])
async def brands_list(db: DbDep, _: StaffUser):
    return list(await db.scalars(select(Brand).order_by(Brand.name)))


@router.post("/brands", response_model=BrandOut, status_code=201)
async def brands_create(data: BrandIn, db: DbDep, _: StaffUser):
    await _slug_free(db, Brand, data.slug)
    obj = Brand(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.patch("/brands/{obj_id}", response_model=BrandOut)
async def brands_update(obj_id: int, data: BrandPatch, db: DbDep, _: StaffUser):
    obj = await _get_or_404(db, Brand, obj_id)
    if data.slug and data.slug != obj.slug:
        await _slug_free(db, Brand, data.slug, obj_id)
    _apply(obj, data)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/brands/{obj_id}", status_code=204)
async def brands_delete(obj_id: int, db: DbDep, _: StaffUser):
    await _delete(db, await _get_or_404(db, Brand, obj_id))


# ─── Products ──────────────────────────────────────────────
@router.get("/products", response_model=Page[ProductListOut])
async def products_list(
    db: DbDep,
    _: StaffUser,
    q: str | None = None,
    category_id: int | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=200),
):
    stmt = select(Product).order_by(Product.id.desc())
    if q:
        stmt = stmt.where(Product.name.ilike(f"%{q.strip()}%"))
    if category_id:
        stmt = stmt.where(Product.category_id == category_id)
    return await _paginated(db, stmt, ProductListOut, page, per_page)


@router.get("/products/{obj_id}", response_model=ProductOut)
async def products_get(obj_id: int, db: DbDep, _: StaffUser):
    return await _get_or_404(db, Product, obj_id)


@router.post("/products", response_model=ProductOut, status_code=201)
async def products_create(data: ProductIn, db: DbDep, _: StaffUser):
    await _slug_free(db, Product, data.slug)
    if not await db.get(Category, data.category_id):
        raise HTTPException(422, "category_id not found")
    if not await db.get(Brand, data.brand_id):
        raise HTTPException(422, "brand_id not found")
    payload = data.model_dump()
    payload["specs"] = [s for s in payload["specs"]]
    obj = Product(**payload)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.patch("/products/{obj_id}", response_model=ProductOut)
async def products_update(obj_id: int, data: ProductPatch, db: DbDep, _: StaffUser):
    obj = await _get_or_404(db, Product, obj_id)
    if data.slug and data.slug != obj.slug:
        await _slug_free(db, Product, data.slug, obj_id)
    if data.category_id and not await db.get(Category, data.category_id):
        raise HTTPException(422, "category_id not found")
    if data.brand_id and not await db.get(Brand, data.brand_id):
        raise HTTPException(422, "brand_id not found")
    _apply(obj, data)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/products/{obj_id}", status_code=204)
async def products_delete(obj_id: int, db: DbDep, _: StaffUser):
    await _delete(db, await _get_or_404(db, Product, obj_id))


# ─── Masters ───────────────────────────────────────────────
@router.get("/masters", response_model=Page[MasterOut])
async def masters_list(
    db: DbDep,
    _: StaffUser,
    q: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=200),
):
    stmt = select(Master).order_by(Master.id.desc())
    if q:
        stmt = stmt.where(Master.name.ilike(f"%{q.strip()}%"))
    return await _paginated(db, stmt, MasterOut, page, per_page)


@router.get("/masters/{obj_id}", response_model=MasterOut)
async def masters_get(obj_id: int, db: DbDep, _: StaffUser):
    return await _get_or_404(db, Master, obj_id)


@router.post("/masters", response_model=MasterOut, status_code=201)
async def masters_create(data: MasterIn, db: DbDep, _: StaffUser):
    await _slug_free(db, Master, data.slug)
    obj = Master(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.patch("/masters/{obj_id}", response_model=MasterOut)
async def masters_update(obj_id: int, data: MasterPatch, db: DbDep, _: StaffUser):
    obj = await _get_or_404(db, Master, obj_id)
    if data.slug and data.slug != obj.slug:
        await _slug_free(db, Master, data.slug, obj_id)
    _apply(obj, data)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/masters/{obj_id}", status_code=204)
async def masters_delete(obj_id: int, db: DbDep, _: StaffUser):
    await _delete(db, await _get_or_404(db, Master, obj_id))


# ─── Services ──────────────────────────────────────────────
@router.get("/services", response_model=list[ServiceOut])
async def services_list(db: DbDep, _: StaffUser):
    return list(await db.scalars(select(Service).order_by(Service.position, Service.id)))


@router.get("/services/{obj_id}", response_model=ServiceOut)
async def services_get(obj_id: int, db: DbDep, _: StaffUser):
    return await _get_or_404(db, Service, obj_id)


@router.post("/services", response_model=ServiceOut, status_code=201)
async def services_create(data: ServiceIn, db: DbDep, _: StaffUser):
    await _slug_free(db, Service, data.slug)
    obj = Service(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.patch("/services/{obj_id}", response_model=ServiceOut)
async def services_update(obj_id: int, data: ServicePatch, db: DbDep, _: StaffUser):
    obj = await _get_or_404(db, Service, obj_id)
    if data.slug and data.slug != obj.slug:
        await _slug_free(db, Service, data.slug, obj_id)
    _apply(obj, data)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/services/{obj_id}", status_code=204)
async def services_delete(obj_id: int, db: DbDep, _: StaffUser):
    await _delete(db, await _get_or_404(db, Service, obj_id))


# ─── Vacancies ─────────────────────────────────────────────
@router.get("/vacancies", response_model=list[VacancyOut])
async def vacancies_list(db: DbDep, _: StaffUser):
    return list(await db.scalars(select(Vacancy).order_by(Vacancy.id.desc())))


@router.get("/vacancies/{obj_id}", response_model=VacancyOut)
async def vacancies_get(obj_id: int, db: DbDep, _: StaffUser):
    return await _get_or_404(db, Vacancy, obj_id)


@router.post("/vacancies", response_model=VacancyOut, status_code=201)
async def vacancies_create(data: VacancyIn, db: DbDep, _: StaffUser):
    await _slug_free(db, Vacancy, data.slug)
    obj = Vacancy(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.patch("/vacancies/{obj_id}", response_model=VacancyOut)
async def vacancies_update(obj_id: int, data: VacancyPatch, db: DbDep, _: StaffUser):
    obj = await _get_or_404(db, Vacancy, obj_id)
    if data.slug and data.slug != obj.slug:
        await _slug_free(db, Vacancy, data.slug, obj_id)
    _apply(obj, data)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/vacancies/{obj_id}", status_code=204)
async def vacancies_delete(obj_id: int, db: DbDep, _: StaffUser):
    await _delete(db, await _get_or_404(db, Vacancy, obj_id))


# ─── Articles ──────────────────────────────────────────────
@router.get("/articles", response_model=list[ArticleOut])
async def articles_list(db: DbDep, _: StaffUser):
    return list(
        await db.scalars(select(Article).order_by(Article.published_on.desc(), Article.id.desc()))
    )


@router.get("/articles/{obj_id}", response_model=ArticleOut)
async def articles_get(obj_id: int, db: DbDep, _: StaffUser):
    return await _get_or_404(db, Article, obj_id)


@router.post("/articles", response_model=ArticleOut, status_code=201)
async def articles_create(data: ArticleIn, db: DbDep, _: StaffUser):
    await _slug_free(db, Article, data.slug)
    obj = Article(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.patch("/articles/{obj_id}", response_model=ArticleOut)
async def articles_update(obj_id: int, data: ArticlePatch, db: DbDep, _: StaffUser):
    obj = await _get_or_404(db, Article, obj_id)
    if data.slug and data.slug != obj.slug:
        await _slug_free(db, Article, data.slug, obj_id)
    _apply(obj, data)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/articles/{obj_id}", status_code=204)
async def articles_delete(obj_id: int, db: DbDep, _: StaffUser):
    await _delete(db, await _get_or_404(db, Article, obj_id))


# ─── FAQ ───────────────────────────────────────────────────
@router.get("/faq", response_model=list[FaqOut])
async def faq_list(db: DbDep, _: StaffUser, section: Literal["general", "services"] | None = None):
    stmt = select(FaqItem).order_by(FaqItem.section, FaqItem.position, FaqItem.id)
    if section:
        stmt = stmt.where(FaqItem.section == section)
    return list(await db.scalars(stmt))


@router.post("/faq", response_model=FaqOut, status_code=201)
async def faq_create(data: FaqIn, db: DbDep, _: StaffUser):
    obj = FaqItem(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.patch("/faq/{obj_id}", response_model=FaqOut)
async def faq_update(obj_id: int, data: FaqPatch, db: DbDep, _: StaffUser):
    obj = await _get_or_404(db, FaqItem, obj_id)
    _apply(obj, data)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/faq/{obj_id}", status_code=204)
async def faq_delete(obj_id: int, db: DbDep, _: StaffUser):
    await _delete(db, await _get_or_404(db, FaqItem, obj_id))
