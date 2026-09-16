from fastapi import APIRouter

from app.core.deps import DbDep
from app.schemas.calculator import CalcIn, CalcOut
from app.schemas.leads import LeadCreate
from app.services import calculator as calc_service
from app.api.leads import create_lead

router = APIRouter()


@router.post("", response_model=CalcOut)
async def calculate(data: CalcIn, db: DbDep) -> CalcOut:
    result = calc_service.estimate(data)

    if data.phone.strip():
        lead = await create_lead(
            db,
            LeadCreate(
                kind="calculator",
                source="site",
                name=data.name,
                phone=data.phone,
                message=(
                    f"{result.room_label}, {data.area:g} м². "
                    f"Работы: {', '.join(line.label for line in result.breakdown)}. "
                    f"Ориентир: {result.total_min:,}–{result.total_max:,} ₸".replace(",", " ")
                ),
                payload={
                    "room": data.room,
                    "area": data.area,
                    "works": list(data.works),
                    "finish": data.finish,
                    "estimate": result.model_dump(),
                },
            ),
        )
        result.lead_number = lead.number

    return result
