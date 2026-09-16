"""RemontHub Telegram bot.

A thin front door: it collects a short request + phone number from the user and
creates a lead through the API (`POST /api/leads`, source=telegram). The same
leads land in the admin CRM as the website's.

Runs in long-polling mode so it needs no public URL. If ``TELEGRAM_BOT_TOKEN``
is empty the process idles (so `docker compose up` still works without a token).
"""
from __future__ import annotations

import asyncio
import logging

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from bot.config import settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("remonthub.bot")

dp = Dispatcher()

KINDS = {
    "🧱 Заказать материалы": "materials",
    "🛠 Вызвать мастера": "master",
    "🏠 Ремонт под ключ": "turnkey",
    "💬 Задать вопрос": "support",
}

MENU = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=label)] for label in KINDS],
    resize_keyboard=True,
    input_field_placeholder="Выберите, с чем помочь",
)


class Flow(StatesGroup):
    describing = State()
    phone = State()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Здравствуйте! Это RemontHub — материалы, мастера и ремонт под ключ в Астане.\n"
        "Выберите, что нужно, и опишите задачу — менеджер свяжется с вами.",
        reply_markup=MENU,
    )


@dp.message(F.text.in_(KINDS.keys()))
async def picked(message: Message, state: FSMContext) -> None:
    await state.update_data(kind=KINDS[message.text])
    await state.set_state(Flow.describing)
    await message.answer(
        "Опишите задачу в одном сообщении: что за помещение, площадь, сроки, пожелания.",
        reply_markup=ReplyKeyboardRemove(),
    )


@dp.message(Flow.describing, F.text)
async def described(message: Message, state: FSMContext) -> None:
    await state.update_data(message=message.text.strip())
    await state.set_state(Flow.phone)
    share = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Отправить мой номер", request_contact=True)]],
        resize_keyboard=True,
    )
    await message.answer("Оставьте номер телефона для связи:", reply_markup=share)


@dp.message(Flow.phone, F.contact | F.text)
async def got_phone(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    phone = message.contact.phone_number if message.contact else (message.text or "").strip()
    name = " ".join(
        filter(None, [message.from_user.first_name, message.from_user.last_name])
    ) or (message.from_user.username or "Telegram")

    payload = {
        "kind": data.get("kind", "other"),
        "source": "telegram",
        "name": name,
        "phone": phone,
        "message": data.get("message", ""),
        "payload": {"chat_id": message.chat.id, "username": message.from_user.username},
    }

    try:
        async with httpx.AsyncClient(base_url=settings.api_base_url, timeout=10) as client:
            resp = await client.post("/api/leads", json=payload)
            resp.raise_for_status()
            number = resp.json().get("number", "—")
        text = (
            f"Готово! Заявка *{number}* принята.\n"
            "Менеджер перезвонит в рабочее время (09:00–20:00)."
        )
    except Exception as exc:  # pragma: no cover
        log.exception("lead submit failed: %s", exc)
        text = "Заявку записал, но связь с системой сейчас нестабильна — менеджер всё равно получит её."

    await state.clear()
    await message.answer(text, parse_mode="Markdown", reply_markup=MENU)


@dp.message(F.text)
async def fallback(message: Message) -> None:
    await message.answer("Выберите пункт меню ниже, чтобы оставить заявку.", reply_markup=MENU)


async def main() -> None:
    if not settings.telegram_bot_token:
        log.warning("TELEGRAM_BOT_TOKEN is not set — bot is idling. Set it in .env to enable.")
        while True:
            await asyncio.sleep(3600)

    bot = Bot(settings.telegram_bot_token)
    log.info("Bot starting in long-polling mode…")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
