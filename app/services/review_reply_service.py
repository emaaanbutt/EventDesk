from __future__ import annotations

from uuid import UUID

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.role_policy import Action
from app.models.enums import NotificationCategory
from app.models.users import User
from app.repositories.event_repository import EventRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.review_reply_repository import ReviewReplyRepository
from app.schemas.review_replies import ReviewReplyCreate, ReviewReplyResponse
from app.services import notification_service
from app.services.authorization_service import authorize_db


def _require_available(actor: User) -> None:
    if not actor.is_active or actor.deleted_at is not None:
        raise HTTPException(status_code=403, detail="User account is unavailable")


async def reply_to_review(
    actor: User,
    review_id: UUID,
    payload: ReviewReplyCreate,
    db: AsyncSession,
    background_tasks: BackgroundTasks,
) -> ReviewReplyResponse:
    _require_available(actor)
    review = await ReviewRepository.get_by_id(review_id, db)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    event = await EventRepository.get_by_id(review.event_id, db)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    await authorize_db(actor, Action.reviews_reply, db, owner_id=event.organizer_id)

    if await ReviewReplyRepository.get_by_author(review.id, actor.id, db) is not None:
        raise HTTPException(status_code=409, detail="You have already replied to this review")

    try:
        reply = await ReviewReplyRepository.create(review.id, actor.id, payload.comment, db)
        response = ReviewReplyResponse.model_validate(reply)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Reply could not be created") from None

    if review.author_id != actor.id:
        background_tasks.add_task(
            notification_service.save_notifications_in_background,
            user_ids=[review.author_id],
            category=NotificationCategory.review,
            title="New reply to your review",
            message=f"Your review for {event.title} received a reply.",
            event_id=event.id,
            booking_id=None,
            review_id=review.id,
        )
    return response


async def list_review_replies(review_id: UUID, db: AsyncSession) -> list[ReviewReplyResponse]:
    review = await ReviewRepository.get_by_id(review_id, db)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    replies = await ReviewReplyRepository.list_for_review(review_id, db)
    return [ReviewReplyResponse.model_validate(reply) for reply in replies]
