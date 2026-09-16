from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select

from app.core.deps import DbDep
from app.models import Article
from app.schemas.common import Page
from app.schemas.content import ArticleListOut, ArticleOut

router = APIRouter()


@router.get("", response_model=Page[ArticleListOut])
async def list_articles(
    db: DbDep,
    category: str | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=12, ge=1, le=200),
) -> Page[ArticleListOut]:
    stmt = select(Article).where(Article.is_published.is_(True))
    if category:
        stmt = stmt.where(Article.category == category)
    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = (
        stmt.order_by(Article.published_on.desc(), Article.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    rows = list(await db.scalars(stmt))
    return Page.build(
        [ArticleListOut.model_validate(r, from_attributes=True) for r in rows], total, page, per_page
    )


@router.get("/categories", response_model=list[str])
async def article_categories(db: DbDep) -> list[str]:
    rows = await db.scalars(select(Article.category).distinct().order_by(Article.category))
    return [c for c in rows if c]


@router.get("/{slug}", response_model=ArticleOut)
async def get_article(slug: str, db: DbDep) -> Article:
    article = await db.scalar(select(Article).where(Article.slug == slug))
    if not article:
        raise HTTPException(404, "Article not found")
    return article
