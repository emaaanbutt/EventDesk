from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review_replies import ReviewReply


class ReviewReplyRepository:
    @staticmethod
    async def get_by_author(review_id: UUID, author_id: UUID, db: AsyncSession) -> ReviewReply | None:
        result = await db.execute(
            select(ReviewReply).where(
                ReviewReply.review_id == review_id,
                ReviewReply.author_id == author_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(review_id: UUID, author_id: UUID, comment: str, db: AsyncSession) -> ReviewReply:
        reply = ReviewReply(review_id=review_id, author_id=author_id, comment=comment)
        db.add(reply)
        await db.flush()
        await db.refresh(reply, attribute_names=["created_at", "updated_at"])
        return reply

    @staticmethod
    async def list_for_review(review_id: UUID, db: AsyncSession) -> list[ReviewReply]:
        result = await db.execute(
            select(ReviewReply)
            .where(ReviewReply.review_id == review_id, ReviewReply.deleted_at.is_(None))
            .order_by(ReviewReply.created_at.asc(), ReviewReply.id.asc())
        )
        return list(result.scalars().all())
