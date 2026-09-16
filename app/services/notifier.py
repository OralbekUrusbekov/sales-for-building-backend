"""Very small notification helper.

Writes an admin-facing Notification row and pushes a short message onto a Redis
list (``remonthub:notifications``) that a bot or dashboard can tail. Failures to
reach Redis are swallowed — notifications must never break the request.
"""
from __future__ import annotations

import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import redis_client
from app.models import Notification

log = logging.getLogger("remonthub.notifier")

CHANNEL = "remonthub:notifications"


async def notify(db: AsyncSession, *, type: str, title: str, body: str = "") -> Notification:
    row = Notification(type=type, title=title, body=body)
    db.add(row)
    await db.flush()

    try:
        await redis_client.lpush(
            CHANNEL, json.dumps({"type": type, "title": title, "body": body}, ensure_ascii=False)
        )
        await redis_client.ltrim(CHANNEL, 0, 199)
    except Exception as exc:  # pragma: no cover - best effort
        log.warning("redis notify failed: %s", exc)

    return row
