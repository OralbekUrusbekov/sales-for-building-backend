import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select

from app.core.deps import DbDep, StaffUser, require_roles
from app.core.redis import redis_client
from app.models import Deal, Lead, Master, Notification, Order, Product, Review, User
from app.models.review import STATUS_PENDING
from app.schemas.admin import DashboardOut, NotificationOut
from app.schemas.auth import UserOut
from app.schemas.common import Page
from app.services.notifier import CHANNEL

router = APIRouter()


@router.get("/dashboard", response_model=DashboardOut)
async def dashboard(db: DbDep, _: StaffUser) -> DashboardOut:
    async def count(model, *where) -> int:
        stmt = select(func.count()).select_from(model)
        for w in where:
            stmt = stmt.where(w)
        return await db.scalar(stmt) or 0

    revenue = await db.scalar(
        select(func.coalesce(func.sum(Order.total), 0)).where(Order.status == "done")
    )
    pipeline = await db.scalar(
        select(func.coalesce(func.sum(Deal.amount), 0)).where(Deal.stage.notin_(("done", "lost")))
    )

    return DashboardOut(
        leads_new=await count(Lead, Lead.status == "new"),
        leads_total=await count(Lead),
        orders_new=await count(Order, Order.status == "new"),
        orders_total=await count(Order),
        revenue_done=int(revenue or 0),
        deals_open=await count(Deal, Deal.stage.notin_(("done", "lost"))),
        deals_pipeline=int(pipeline or 0),
        reviews_pending=await count(Review, Review.status == STATUS_PENDING),
        products=await count(Product),
        masters=await count(Master),
    )


@router.get("/notifications", response_model=Page[NotificationOut])
async def notifications(
    db: DbDep,
    _: StaffUser,
    unread_only: bool = False,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=30, ge=1, le=500),
) -> Page[NotificationOut]:
    stmt = select(Notification)
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = list(
        await db.scalars(
            stmt.order_by(Notification.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
    )
    return Page.build(
        [NotificationOut.model_validate(r, from_attributes=True) for r in rows], total, page, per_page
    )


@router.post("/notifications/{notification_id}/read", response_model=NotificationOut)
async def mark_read(notification_id: int, db: DbDep, _: StaffUser) -> Notification:
    row = await db.get(Notification, notification_id)
    if not row:
        raise HTTPException(404, "Notification not found")
    row.is_read = True
    await db.commit()
    await db.refresh(row)
    return row


@router.post("/notifications/read-all")
async def mark_all_read(db: DbDep, _: StaffUser) -> dict:
    rows = list(await db.scalars(select(Notification).where(Notification.is_read.is_(False))))
    for row in rows:
        row.is_read = True
    await db.commit()
    return {"updated": len(rows)}


@router.get("/notifications/feed")
async def notifications_feed(_: StaffUser, limit: int = Query(default=20, ge=1, le=200)) -> list[dict]:
    """Latest notifications pushed to Redis (for a live ticker)."""
    try:
        raw = await redis_client.lrange(CHANNEL, 0, limit - 1)
    except Exception:
        return []
    out = []
    for item in raw:
        try:
            out.append(json.loads(item))
        except json.JSONDecodeError:
            continue
    return out


@router.get("/users", response_model=Page[UserOut])
async def list_users(
    db: DbDep,
    _: Annotated[User, Depends(require_roles("admin"))],
    role: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=30, ge=1, le=500),
) -> Page[UserOut]:
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = list(
        await db.scalars(
            stmt.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        )
    )
    return Page.build(
        [UserOut.model_validate(r, from_attributes=True) for r in rows], total, page, per_page
    )
