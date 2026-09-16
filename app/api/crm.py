from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.core.deps import DbDep, StaffUser
from app.models import Deal
from app.schemas.common import Page
from app.schemas.crm import (
    BoardColumn,
    CrmBoard,
    DealCreate,
    DealOut,
    DealUpdate,
    StageOut,
)
from app.services.numbering import next_deal_code

router = APIRouter()

STAGES: list[StageOut] = [
    StageOut(key="new", label="Новая", tone="new"),
    StageOut(key="contact", label="Контакт", tone="new"),
    StageOut(key="measure", label="Замер", tone="warm"),
    StageOut(key="estimate", label="Смета", tone="warm"),
    StageOut(key="contract", label="Договор", tone="work"),
    StageOut(key="inwork", label="В работе", tone="work"),
    StageOut(key="done", label="Завершена", tone="won"),
    StageOut(key="lost", label="Отказ", tone="lost"),
]
MANAGERS = ["Андрей Ким", "Салтанат Б.", "Ержан Т.", "Динара О."]
_VALID_STAGES = {s.key for s in STAGES}


@router.get("/stages", response_model=list[StageOut])
async def list_stages(_: StaffUser) -> list[StageOut]:
    return STAGES


@router.get("/managers", response_model=list[str])
async def list_managers(_: StaffUser) -> list[str]:
    return MANAGERS


@router.get("/board", response_model=CrmBoard)
async def board(db: DbDep, _: StaffUser, manager: str | None = None) -> CrmBoard:
    stmt = select(Deal)
    if manager:
        stmt = stmt.where(Deal.manager == manager)
    deals = list(await db.scalars(stmt.order_by(Deal.created_at.desc())))

    columns: list[BoardColumn] = []
    for stage in STAGES:
        bucket = [d for d in deals if d.stage == stage.key]
        columns.append(
            BoardColumn(
                stage=stage,
                count=len(bucket),
                total=sum(d.amount for d in bucket),
                deals=[DealOut.model_validate(d, from_attributes=True) for d in bucket],
            )
        )
    open_total = sum(d.amount for d in deals if d.stage not in ("done", "lost"))
    won_total = sum(d.amount for d in deals if d.stage == "done")
    return CrmBoard(columns=columns, managers=MANAGERS, open_total=open_total, won_total=won_total)


@router.get("", response_model=Page[DealOut])
async def list_deals(
    db: DbDep,
    _: StaffUser,
    stage: str | None = None,
    manager: str | None = None,
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
) -> Page[DealOut]:
    stmt = select(Deal)
    if stage:
        stmt = stmt.where(Deal.stage == stage)
    if manager:
        stmt = stmt.where(Deal.manager == manager)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            Deal.client.ilike(like) | Deal.phone.ilike(like) | Deal.code.ilike(like) | Deal.type.ilike(like)
        )
    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = list(
        await db.scalars(
            stmt.order_by(Deal.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        )
    )
    return Page.build(
        [DealOut.model_validate(r, from_attributes=True) for r in rows], total, page, per_page
    )


@router.post("", response_model=DealOut, status_code=status.HTTP_201_CREATED)
async def create_deal(data: DealCreate, db: DbDep, _: StaffUser) -> Deal:
    deal = Deal(code=await next_deal_code(db), **data.model_dump())
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal


@router.get("/{deal_id}", response_model=DealOut)
async def get_deal(deal_id: int, db: DbDep, _: StaffUser) -> Deal:
    deal = await db.get(Deal, deal_id)
    if not deal:
        raise HTTPException(404, "Deal not found")
    return deal


@router.patch("/{deal_id}", response_model=DealOut)
async def update_deal(deal_id: int, data: DealUpdate, db: DbDep, _: StaffUser) -> Deal:
    deal = await db.get(Deal, deal_id)
    if not deal:
        raise HTTPException(404, "Deal not found")
    payload = data.model_dump(exclude_unset=True)
    if "stage" in payload and payload["stage"] not in _VALID_STAGES:
        raise HTTPException(422, "Unknown stage")
    for key, value in payload.items():
        setattr(deal, key, value)
    await db.commit()
    await db.refresh(deal)
    return deal


@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(deal_id: int, db: DbDep, _: StaffUser) -> None:
    deal = await db.get(Deal, deal_id)
    if not deal:
        raise HTTPException(404, "Deal not found")
    await db.delete(deal)
    await db.commit()
