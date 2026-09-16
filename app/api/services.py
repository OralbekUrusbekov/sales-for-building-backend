from fastapi import APIRouter, HTTPException
from sqlalchemy import or_, select

from app.core.deps import DbDep
from app.models import Service
from app.schemas.content import ServiceOut

router = APIRouter()


@router.get("", response_model=list[ServiceOut])
async def list_services(db: DbDep) -> list[Service]:
    return list(
        await db.scalars(
            select(Service)
            .where(Service.is_active.is_(True))
            .order_by(Service.position, Service.id)
        )
    )


@router.get("/{key}", response_model=ServiceOut)
async def get_service(key: str, db: DbDep) -> Service:
    stmt = select(Service).where(Service.slug == key)
    if key.isdigit():
        stmt = select(Service).where(or_(Service.slug == key, Service.id == int(key)))
    service = await db.scalar(stmt)
    if not service:
        raise HTTPException(404, "Service not found")
    return service
