from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reviews import Review

class ReviewRepository:
    @staticmethod
    async def get_by_id(review_id: UUID, db: AsyncSession) -> Review | None:
        result = await db.execute(
            select(Review)
            .where(Review.id == review_id, Review.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_author_and_event(author_id: UUID, event_id: UUID, db: AsyncSession) -> Review | None:
        result = await db.execute(
            select(Review)
            .where(Review.author_id == author_id, Review.event_id == event_id)
        )

        return result.scalar_one_or_none()


    @staticmethod
    async def create_review(event_id: UUID, author_id: UUID, rating: int, comment: str, db: AsyncSession) -> Review:
        review = Review(
            author_id = author_id,
            event_id = event_id,
            rating = rating,
            comment = comment
        )
        db.add(review)
        await db.flush()
        await db.refresh(review)
        return review

    @staticmethod
    async def update_review(review: Review, changes: dict[str, Any], db: AsyncSession) -> Review:
        for field, val in changes.items():
            setattr(review, field, val)

        await db.flush()
        await db.refresh(review, attribute_names=["updated_at"])
        return review

    @staticmethod
    async def soft_delete(review: Review, db: AsyncSession) -> None:
        deleted_at = datetime.now(timezone.utc)
        review.deleted_at = deleted_at
        await db.flush()

    @staticmethod
    async def list_reviews_for_event(event_id: UUID, page: int, page_size: int, db: AsyncSession) -> tuple[list[Review], int]:
        conditions = (Review.event_id == event_id, Review.deleted_at.is_(None))
        count_result = await db.execute(select(func.count(Review.id)).where(*conditions))
        result = await db.execute(
            select(Review)
            .where(*conditions)
            .order_by(Review.created_at.desc(), Review.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        return list(result.scalars().all()), count_result.scalar_one()
