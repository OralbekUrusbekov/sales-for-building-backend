from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.core.deps import DbDep, StaffUser
from app.models import Review
from app.models.review import STATUS_PENDING, STATUS_PUBLISHED, STATUS_REJECTED
from app.schemas.common import Page
from app.schemas.reviews import RatingBucket, ReviewIn, ReviewOut, ReviewStats
from app.services.notifier import notify

router = APIRouter()


@router.get("", response_model=list[ReviewOut])
async def list_reviews(
    db: DbDep,
    target_type: Literal["product", "master", "service"],
    target_id: str,
) -> list[Review]:
    rows = await db.scalars(
        select(Review)
        .where(
            Review.target_type == target_type,
            Review.target_id == target_id,
            Review.status == STATUS_PUBLISHED,
        )
        .order_by(Review.created_at.desc())
    )
    return list(rows)


@router.get("/latest", response_model=list[ReviewOut])
async def latest_reviews(db: DbDep, limit: int = Query(default=8, ge=1, le=50)) -> list[Review]:
    rows = await db.scalars(
        select(Review)
        .where(Review.status == STATUS_PUBLISHED)
        .order_by(Review.created_at.desc())
        .limit(limit)
    )
    return list(rows)


@router.get("/stats", response_model=ReviewStats)
async def review_stats(
    db: DbDep,
    target_type: Literal["product", "master", "service"],
    target_id: str,
) -> ReviewStats:
    rows = list(
        await db.scalars(
            select(Review).where(
                Review.target_type == target_type,
                Review.target_id == target_id,
                Review.status == STATUS_PUBLISHED,
            )
        )
    )
    total = len(rows)
    avg = round(sum(r.rating for r in rows) / total, 2) if total else 0.0
    dist = [
        RatingBucket(
            star=star,
            count=(c := sum(1 for r in rows if r.rating == star)),
            pct=round(c / total * 100) if total else 0,
        )
        for star in (5, 4, 3, 2, 1)
    ]
    return ReviewStats(total=total, avg=avg, dist=dist)


@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review(data: ReviewIn, db: DbDep) -> Review:
    review = Review(
        target_type=data.target_type,
        target_id=data.target_id,
        author_name=data.author_name,
        rating=data.rating,
        text=data.text,
        photos=data.photos,
        status=STATUS_PENDING,
    )
    db.add(review)
    await notify(
        db,
        type="review",
        title="Новый отзыв на модерации",
        body=f"{data.author_name} · {data.rating}★ · {data.target_type}/{data.target_id}",
    )
    await db.commit()
    await db.refresh(review)
    return review


# ─── moderation (staff) ────────────────────────────────────
@router.get("/moderation", response_model=Page[ReviewOut])
async def moderation_queue(
    db: DbDep,
    _: StaffUser,
    status_filter: Literal["pending", "published", "rejected"] = Query(
        default="pending", alias="status"
    ),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=30, ge=1, le=500),
) -> Page[ReviewOut]:
    stmt = select(Review).where(Review.status == status_filter)
    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = list(
        await db.scalars(
            stmt.order_by(Review.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        )
    )
    return Page.build(
        [ReviewOut.model_validate(r, from_attributes=True) for r in rows], total, page, per_page
    )


@router.post("/{review_id}/publish", response_model=ReviewOut)
async def publish_review(review_id: int, db: DbDep, _: StaffUser) -> Review:
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    review.status = STATUS_PUBLISHED
    await db.commit()
    await db.refresh(review)
    return review


@router.post("/{review_id}/reject", response_model=ReviewOut)
async def reject_review(review_id: int, db: DbDep, _: StaffUser) -> Review:
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(404, "Review not found")
    review.status = STATUS_REJECTED
    await db.commit()
    await db.refresh(review)
    return review
