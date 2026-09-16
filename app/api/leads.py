from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.core.deps import DbDep, StaffUser
from app.models import Lead
from app.schemas.common import Page
from app.schemas.leads import LeadCreate, LeadOut, LeadStatusIn
from app.services.notifier import notify
from app.services.numbering import next_lead_number

router = APIRouter()

_KIND_LABEL = {
    "materials": "Заказ материалов",
    "master": "Вызов мастера",
    "service": "Услуга",
    "turnkey": "Ремонт под ключ",
    "calculator": "Смета из калькулятора",
    "support": "Поддержка",
    "other": "Заявка",
}


async def create_lead(db: DbDep, data: LeadCreate) -> Lead:
    lead = Lead(
        number=await next_lead_number(db, data.source),
        source=data.source,
        kind=data.kind,
        name=data.name,
        phone=data.phone,
        message=data.message,
        payload=data.payload,
        status="new",
    )
    db.add(lead)
    await notify(
        db,
        type="lead",
        title=f"Новая заявка · {_KIND_LABEL.get(data.kind, 'Заявка')}",
        body=f"{lead.number} · {data.name or '—'} · {data.phone or '—'} · {data.source}",
    )
    await db.commit()
    await db.refresh(lead)
    return lead


@router.post("", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
async def submit_lead(data: LeadCreate, db: DbDep) -> Lead:
    return await create_lead(db, data)


@router.get("", response_model=Page[LeadOut])
async def list_leads(
    db: DbDep,
    _: StaffUser,
    source: Literal["site", "telegram", "phone"] | None = None,
    kind: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=30, ge=1, le=500),
) -> Page[LeadOut]:
    stmt = select(Lead)
    if source:
        stmt = stmt.where(Lead.source == source)
    if kind:
        stmt = stmt.where(Lead.kind == kind)
    if status_filter:
        stmt = stmt.where(Lead.status == status_filter)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(Lead.name.ilike(like) | Lead.phone.ilike(like) | Lead.number.ilike(like))
    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = list(
        await db.scalars(
            stmt.order_by(Lead.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        )
    )
    return Page.build(
        [LeadOut.model_validate(r, from_attributes=True) for r in rows], total, page, per_page
    )


@router.patch("/{lead_id}/status", response_model=LeadOut)
async def set_lead_status(lead_id: int, data: LeadStatusIn, db: DbDep, _: StaffUser) -> Lead:
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    lead.status = data.status
    await db.commit()
    await db.refresh(lead)
    return lead
