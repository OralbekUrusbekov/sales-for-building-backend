from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, or_, select

from app.core.deps import DbDep
from app.models import Master
from app.schemas.common import Page
from app.schemas.masters import MasterOut

router = APIRouter()


@router.get("", response_model=Page[MasterOut])
async def list_masters(
    db: DbDep,
    q: str | None = None,
    specialty: str | None = Query(default=None, description="match against specialty list"),
    district: str | None = None,
    available: bool | None = None,
    verified: bool | None = None,
    sort: str = Query(default="rating", pattern="^(rating|jobs|rate_asc|rate_desc)$"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=24, ge=1, le=500),
) -> Page[MasterOut]:
    stmt = select(Master)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Master.name.ilike(like), Master.bio.ilike(like)))
    if specialty:
        stmt = stmt.where(Master.specialty.contains([specialty]))
    if district:
        stmt = stmt.where(Master.district == district)
    if available is not None:
        stmt = stmt.where(Master.available.is_(available))
    if verified is not None:
        stmt = stmt.where(Master.verified.is_(verified))

    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    order = {
        "rating": (Master.rating.desc(), Master.review_count.desc()),
        "jobs": (Master.jobs.desc(),),
        "rate_asc": (Master.rate.asc(),),
        "rate_desc": (Master.rate.desc(),),
    }[sort]
    stmt = stmt.order_by(*order).offset((page - 1) * per_page).limit(per_page)
    rows = list(await db.scalars(stmt))
    return Page.build(
        [MasterOut.model_validate(r, from_attributes=True) for r in rows], total, page, per_page
    )


@router.get("/districts", response_model=list[str])
async def list_districts(db: DbDep) -> list[str]:
    rows = await db.scalars(select(Master.district).distinct().order_by(Master.district))
    return [d for d in rows if d]


@router.get("/{key}", response_model=MasterOut)
async def get_master(key: str, db: DbDep) -> Master:
    stmt = select(Master).where(Master.slug == key)
    if key.isdigit():
        stmt = select(Master).where(or_(Master.slug == key, Master.id == int(key)))
    master = await db.scalar(stmt)
    if not master:
        raise HTTPException(404, "Master not found")
    return master
