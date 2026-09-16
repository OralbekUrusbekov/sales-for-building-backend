from fastapi import APIRouter, Header, HTTPException, Request

from app.core.config import settings
from app.core.deps import DbDep
from app.schemas.leads import LeadCreate
from app.api.leads import create_lead

router = APIRouter()

_KEYWORDS = {
    "мастер": "master",
    "материал": "materials",
    "под ключ": "turnkey",
    "смет": "calculator",
    "помощь": "support",
}


def _classify(text: str) -> str:
    low = text.lower()
    for needle, kind in _KEYWORDS.items():
        if needle in low:
            return kind
    return "other"


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    db: DbDep,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict:
    if settings.telegram_webhook_secret:
        if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
            raise HTTPException(403, "Bad webhook secret")

    update = await request.json()
    message = update.get("message") or update.get("edited_message") or {}
    text = (message.get("text") or "").strip()
    chat = message.get("chat") or {}
    contact = message.get("contact") or {}
    from_user = message.get("from") or {}

    name = (
        contact.get("first_name")
        or " ".join(filter(None, [from_user.get("first_name"), from_user.get("last_name")]))
        or chat.get("username")
        or "Telegram"
    )
    phone = contact.get("phone_number", "")

    if not text and not phone:
        return {"ok": True, "skipped": "empty update"}

    lead = await create_lead(
        db,
        LeadCreate(
            kind=_classify(text),
            source="telegram",
            name=name,
            phone=phone,
            message=text,
            payload={"chat_id": chat.get("id"), "username": from_user.get("username")},
        ),
    )
    return {"ok": True, "lead": {"number": lead.number, "kind": lead.kind, "status": lead.status}}
