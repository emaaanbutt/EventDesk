from __future__ import annotations

from uuid import UUID

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.role_policy import Action
from app.models.enums import NotificationCategory
from app.models.events import Event
from app.models.reviews import Review
from app.models.users import User
from app.repositories.booking_repository import BookingRepository
from app.repositories.event_repository import EventRepository
from app.repositories.review_repository import ReviewRepository
from app.schemas.reviews import (
    ReviewCreate,
    ReviewListResponse,
    ReviewReplyCreate,
    ReviewReplyResponse,
    ReviewResponse,
    ReviewUpdate,
)
from app.services import notification_service
from app.services.authorization_service import authorize


def _require_available(actor: User) -> None:
    if not actor.is_active or actor.deleted_at is not None:
        raise HTTPException(status_code=403, detail="User account is unavailable")


async def _get_event_or_404(event_id: UUID, db: AsyncSession) -> Event:
    event = await EventRepository.get_by_id(event_id, db)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


async def _get_review_or_404(review_id: UUID, db: AsyncSession) -> Review:
    review = await ReviewRepository.get_by_id(review_id, db)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


async def create_review(
    actor: User, payload: ReviewCreate, db: AsyncSession, background_tasks: BackgroundTasks
) -> ReviewResponse:
    _require_available(actor)
    authorize(actor, Action.reviews_create)
    event = await _get_event_or_404(payload.event_id, db)

    if not await BookingRepository.has_confirmed_booking(event.id, actor.id, db):
        raise HTTPException(status_code=403, detail="A confirmed booking is required to review this event")
    if await ReviewRepository.get_by_author_and_event(actor.id, event.id, db) is not None:
        raise HTTPException(status_code=409, detail="You have already reviewed this event")

    try:
        review = await ReviewRepository.create_review(
            event.id, actor.id, payload.rating, payload.comment, db
        )
        response = ReviewResponse.model_validate(review)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Review could not be created") from None

    if event.organizer_id != actor.id:
        background_tasks.add_task(
            notification_service.save_notifications_in_background,
            user_ids=[event.organizer_id],
            category=NotificationCategory.review,
            title="New review",
            message=f"Your event {event.title} received a new review.",
            event_id=event.id,
            booking_id=None,
            review_id=review.id,
        )
    return response


async def reply_to_review(
    actor: User,
    review_id: UUID,
    payload: ReviewReplyCreate,
    db: AsyncSession,
    background_tasks: BackgroundTasks,
) -> ReviewReplyResponse:
    _require_available(actor)
    review = await _get_review_or_404(review_id, db)
    event = await _get_event_or_404(review.event_id, db)
    authorize(actor, Action.reviews_reply, owner_id=event.organizer_id)

    if await ReviewRepository.get_reply_by_author(review.id, actor.id, db) is not None:
        raise HTTPException(status_code=409, detail="You have already replied to this review")

    try:
        reply = await ReviewRepository.create_reply(review.id, actor.id, payload.comment, db)
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


async def update_review(
    actor: User, review_id: UUID, payload: ReviewUpdate, db: AsyncSession
) -> ReviewResponse:
    _require_available(actor)
    review = await _get_review_or_404(review_id, db)
    authorize(actor, Action.reviews_edit, owner_id=review.author_id)

    try:
        review = await ReviewRepository.update_review(
            review, payload.model_dump(exclude_unset=True), db
        )
        response = ReviewResponse.model_validate(review)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Review could not be updated") from None
    return response


async def delete_review(actor: User, review_id: UUID, db: AsyncSession) -> None:
    _require_available(actor)
    review = await _get_review_or_404(review_id, db)
    authorize(actor, Action.reviews_delete, owner_id=review.author_id)

    await ReviewRepository.soft_delete(review, db)
    await db.commit()


async def list_event_reviews(
    event_id: UUID, page: int, page_size: int, db: AsyncSession
) -> ReviewListResponse:
    await _get_event_or_404(event_id, db)
    reviews, total = await ReviewRepository.list_reviews_for_event(event_id, page, page_size, db)
    return ReviewListResponse(
        items=[ReviewResponse.model_validate(review) for review in reviews],
        total=total,
        page=page,
        page_size=page_size,
    )


async def list_review_replies(review_id: UUID, db: AsyncSession) -> list[ReviewReplyResponse]:
    await _get_review_or_404(review_id, db)
    replies = await ReviewRepository.list_replies(review_id, db)
    return [ReviewReplyResponse.model_validate(reply) for reply in replies]
