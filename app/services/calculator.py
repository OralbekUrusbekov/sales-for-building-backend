"""Rough renovation estimate — mirrors the frontend calculator wizard.

The numbers are deliberately simple: a per-m² rate for each type of work,
scaled by a room-type coefficient and a finish-level multiplier. Materials are
estimated as a share of the labour cost, plus fixed equipment rental and
consumables. The result is a ±% range, not a binding quote.
"""
from __future__ import annotations

from app.schemas.calculator import CalcIn, CalcLine, CalcOut

ROOM_LABEL: dict[str, str] = {
    "bathroom": "Ванная",
    "kitchen": "Кухня",
    "room": "Комната",
    "corridor": "Коридор",
    "apartment": "Квартира целиком",
}
ROOM_COEF: dict[str, float] = {
    "bathroom": 1.35,
    "kitchen": 1.25,
    "room": 1.0,
    "corridor": 0.9,
    "apartment": 1.1,
}

WORK_LABEL: dict[str, str] = {
    "demolition": "Демонтаж",
    "plaster": "Штукатурка и шпаклёвка",
    "electric": "Электрика",
    "tile": "Плитка",
    "plumbing": "Сантехника",
    "paint": "Покраска и обои",
    "floor": "Напольное покрытие",
    "ceiling": "Потолок",
}
WORK_RATE: dict[str, int] = {  # ₸ per m²
    "demolition": 2200,
    "plaster": 3500,
    "electric": 2800,
    "tile": 6000,
    "plumbing": 4200,
    "paint": 2500,
    "floor": 3200,
    "ceiling": 2600,
}

FINISH_MULT: dict[str, float] = {"econom": 0.85, "standard": 1.0, "premium": 1.4}
MATERIALS_SHARE = 0.8
EQUIPMENT_BASE = 45_000
CONSUMABLES_PER_M2 = 400


def _round(value: float, step: int = 500) -> int:
    return int(round(value / step) * step)


def estimate(data: CalcIn) -> CalcOut:
    room_coef = ROOM_COEF[data.room]
    finish_mult = FINISH_MULT[data.finish]
    area = data.area

    breakdown: list[CalcLine] = []
    works_cost = 0
    for key in dict.fromkeys(data.works):  # de-dupe, keep order
        line = _round(WORK_RATE[key] * area * room_coef * finish_mult)
        works_cost += line
        breakdown.append(CalcLine(key=key, label=WORK_LABEL[key], amount=line))

    materials_cost = _round(works_cost * MATERIALS_SHARE * finish_mult)
    equipment_cost = _round(EQUIPMENT_BASE + CONSUMABLES_PER_M2 * area)

    total = works_cost + materials_cost + equipment_cost
    return CalcOut(
        area=area,
        room_label=ROOM_LABEL[data.room],
        works_cost=works_cost,
        materials_cost=materials_cost,
        equipment_cost=equipment_cost,
        total_min=_round(total * 0.92),
        total_max=_round(total * 1.12),
        breakdown=breakdown,
    )
