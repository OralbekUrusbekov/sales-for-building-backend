from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin

# Single-row table (id=1) holding editable site content as one JSON blob.
DEFAULT_SETTINGS: dict = {
    "contact": {
        "phone": "+7 700 123 45 67",
        "phone_href": "tel:+77001234567",
        "email": "hello@remonthub.kz",
        "address": "Астана, ул. Кабанбай батыра, 15",
        "hours": "Ежедневно 09:00–20:00",
        "whatsapp": "https://wa.me/77001234567",
        "map_link": "https://www.openstreetmap.org/?mlat=51.1801&mlon=71.4460#map=16/51.1801/71.4460",
        "delivery_note": "Доставка по Астане 1–2 дня",
    },
    "hero": {
        "heading": "Ремонт начинается с",
        "accent": "правильного решения",
        "subtitle": "Материалы с доставкой, проверенные мастера и понятная смета — без лишних звонков и переплат.",
        "primary_label": "Рассчитать ремонт",
        "primary_href": "/calculator",
        "secondary_label": "Открыть каталог",
        "secondary_href": "/catalog",
        "bg_image": "https://images.unsplash.com/photo-1503387762-592deb58ef4e?auto=format&fit=crop&w=2000&q=80",
    },
    "trust": [
        {"icon": "truck", "title": "Доставка 1–2 дня", "text": "по Астане, подъём на этаж"},
        {"icon": "badge", "title": "Проверенные мастера", "text": "документы, портфолио, отзывы"},
        {"icon": "clipboard", "title": "Прозрачная смета", "text": "материалы и работы отдельно"},
        {"icon": "return", "title": "Возврат 14 дней", "text": "для неиспользованных товаров"},
    ],
    "company": {
        "name": "RemontHub",
        "about_short": "Склад материалов, база проверенных мастеров и услуги под ключ в одном месте.",
        "founded_year": 2012,
    },
}


class SiteSetting(Base, TimestampMixin):
    __tablename__ = "site_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    data: Mapped[dict] = mapped_column(JSONB, default=dict)
