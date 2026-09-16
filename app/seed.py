"""Idempotent database seeder.

Run standalone:  ``python -m app.seed``
It is safe to run repeatedly — each section is skipped if its table already
holds rows. Pass ``--force`` to wipe the domain tables first.
"""
from __future__ import annotations

import asyncio
import sys
from datetime import date, datetime

from sqlalchemy import delete, func, select

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.core.security import hash_password
from app.models import (
    Article,
    Brand,
    Category,
    Deal,
    FaqItem,
    Master,
    Product,
    Review,
    Service,
    User,
    Vacancy,
)
from app import seed_data as sd


async def _count(db, model) -> int:
    return await db.scalar(select(func.count()).select_from(model)) or 0


async def seed_users(db) -> None:
    email = settings.admin_email.lower()
    existing = await db.scalar(select(User).where(User.email == email))
    if existing:
        return
    db.add(
        User(
            email=email,
            name="Администратор",
            phone="+7 700 123 45 67",
            password_hash=hash_password(settings.admin_password),
            role="admin",
        )
    )
    db.add(
        User(
            email="manager@remonthub.kz",
            name="Менеджер",
            phone="+7 700 000 00 00",
            password_hash=hash_password("manager12345"),
            role="manager",
        )
    )
    print(f"  · users: admin ({email}) + manager")


async def seed_catalog(db) -> None:
    if await _count(db, Product):
        return
    categories, brands, products = sd.build_products()

    cat_by_slug: dict[str, Category] = {}
    for row in categories:
        obj = Category(**row)
        db.add(obj)
        cat_by_slug[row["slug"]] = obj

    brand_by_slug: dict[str, Brand] = {}
    for row in brands:
        obj = Brand(**row)
        db.add(obj)
        brand_by_slug[row["slug"]] = obj

    await db.flush()

    for row in products:
        cat = cat_by_slug[row.pop("category_slug")]
        brand = brand_by_slug[row.pop("brand_slug")]
        db.add(Product(category_id=cat.id, brand_id=brand.id, **row))

    print(f"  · catalog: {len(categories)} categories, {len(brands)} brands, {len(products)} products")


async def seed_masters(db) -> None:
    if await _count(db, Master):
        return
    for row in sd.build_masters():
        db.add(Master(**row))
    print(f"  · masters: {len(sd.MASTERS)}")


async def seed_services(db) -> None:
    if await _count(db, Service):
        return
    for i, row in enumerate(sd.SERVICES):
        db.add(Service(position=i, **row))
    print(f"  · services: {len(sd.SERVICES)}")


async def seed_vacancies(db) -> None:
    if await _count(db, Vacancy):
        return
    for row in sd.VACANCIES:
        db.add(Vacancy(city="Астана", **row))
    print(f"  · vacancies: {len(sd.VACANCIES)}")


async def seed_articles(db) -> None:
    if await _count(db, Article):
        return
    for row in sd.ARTICLES:
        row = dict(row)
        row["published_on"] = date.fromisoformat(row["published_on"])
        db.add(Article(**row))
    print(f"  · articles: {len(sd.ARTICLES)}")


async def seed_reviews(db) -> None:
    if await _count(db, Review):
        return
    for row in sd.build_reviews():
        row = dict(row)
        row["created_at"] = datetime.fromisoformat(row["created_at"])
        db.add(Review(**row))
    print(f"  · reviews: {len(sd.REVIEWS)}")


async def seed_faq(db) -> None:
    if await _count(db, FaqItem):
        return
    for i, row in enumerate(sd.FAQ):
        db.add(FaqItem(position=i, **row))
    print(f"  · faq: {len(sd.FAQ)}")


async def seed_deals(db) -> None:
    if await _count(db, Deal):
        return
    for code, client, phone, dtype, amount, stage, manager, source, created, note in sd.DEALS:
        db.add(
            Deal(
                code=code,
                client=client,
                phone=phone,
                type=dtype,
                amount=amount,
                stage=stage,
                manager=manager,
                source=source,
                note=note,
                created_at=datetime.fromisoformat(created),
            )
        )
    print(f"  · crm deals: {len(sd.DEALS)}")


DOMAIN_TABLES = (Review, Product, Brand, Category, Master, Service, Vacancy, Article, FaqItem, Deal)


async def run(force: bool = False) -> None:
    async with SessionLocal() as db:
        if force:
            print("→ --force: clearing domain tables")
            for model in DOMAIN_TABLES:
                await db.execute(delete(model))
            await db.flush()

        print("→ Seeding…")
        await seed_users(db)
        await seed_catalog(db)
        await seed_masters(db)
        await seed_services(db)
        await seed_vacancies(db)
        await seed_articles(db)
        await seed_reviews(db)
        await seed_faq(db)
        await seed_deals(db)
        await db.commit()
    await engine.dispose()
    print("✓ Seed complete")


if __name__ == "__main__":
    asyncio.run(run(force="--force" in sys.argv))
