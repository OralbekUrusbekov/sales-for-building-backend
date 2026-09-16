from fastapi import APIRouter, HTTPException
from sqlalchemy import or_, select

from app.core.deps import DbDep
from app.models import Vacancy
from app.schemas.content import VacancyOut

router = APIRouter()


@router.get("", response_model=list[VacancyOut])
async def list_vacancies(db: DbDep, open_only: bool = True) -> list[Vacancy]:
    stmt = select(Vacancy).order_by(Vacancy.id)
    if open_only:
        stmt = stmt.where(Vacancy.is_open.is_(True))
    return list(await db.scalars(stmt))


@router.get("/{key}", response_model=VacancyOut)
async def get_vacancy(key: str, db: DbDep) -> Vacancy:
    stmt = select(Vacancy).where(Vacancy.slug == key)
    if key.isdigit():
        stmt = select(Vacancy).where(or_(Vacancy.slug == key, Vacancy.id == int(key)))
    vacancy = await db.scalar(stmt)
    if not vacancy:
        raise HTTPException(404, "Vacancy not found")
    return vacancy
