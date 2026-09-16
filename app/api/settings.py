"""Editable site content (contacts, hero, trust strip…)."""
import copy

from fastapi import APIRouter

from app.core.deps import DbDep, StaffUser
from app.models import DEFAULT_SETTINGS, SiteSetting

router = APIRouter()
manage_router = APIRouter()


def _deep_merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


async def _load(db) -> dict:
    row = await db.get(SiteSetting, 1)
    return _deep_merge(DEFAULT_SETTINGS, row.data if row else {})


@router.get("")
async def get_settings(db: DbDep) -> dict:
    """Public — the current site content (defaults merged with overrides)."""
    return await _load(db)


@manage_router.get("/settings")
async def manage_get_settings(db: DbDep, _: StaffUser) -> dict:
    return await _load(db)


@manage_router.put("/settings")
async def manage_put_settings(payload: dict, db: DbDep, _: StaffUser) -> dict:
    row = await db.get(SiteSetting, 1)
    merged = _deep_merge(DEFAULT_SETTINGS, payload)
    if row is None:
        row = SiteSetting(id=1, data=merged)
        db.add(row)
    else:
        row.data = merged
    await db.commit()
    await db.refresh(row)
    return _deep_merge(DEFAULT_SETTINGS, row.data)
