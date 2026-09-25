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
            .where(Review.author_id == author_id and Review.event_id == event_id)
        )

        return result.scalar_one_or_none()


    @staticmethod
    async def create_review(event_id: UUID, author_id: UUID, rating: int, comment: str, db: AsyncSession) -> Review:
        review = await Review(
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


