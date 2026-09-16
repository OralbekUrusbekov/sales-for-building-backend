from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Deal, Lead, Order


async def next_order_number(db: AsyncSession) -> str:
    year = datetime.now(timezone.utc).year
    count = await db.scalar(select(func.count()).select_from(Order)) or 0
    return f"RH-{year}-{count + 1:05d}"


async def next_lead_number(db: AsyncSession, source: str = "site") -> str:
    prefix = {"site": "RH", "telegram": "RH-TG", "phone": "RH-PH"}.get(source, "RH")
    count = await db.scalar(select(func.count()).select_from(Lead)) or 0
    return f"{prefix}-{count + 1:05d}"


async def next_deal_code(db: AsyncSession) -> str:
    # Continue the D-2xxx sequence used by the seed data.
    top = await db.scalar(select(func.max(Deal.id))) or 0
    return f"D-{2020 + top + 1}"
