from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.role_policy import Action
from app.db.session import AsyncSessionLocal
from app.models.enums import NotificationCategory
from app.models.users import User
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notifications import (
    NotificationFilters,
    NotificationListResponse,
    NotificationReadUpdate,
    NotificationResponse,
)
from app.services.authorization_service import authorize


def _require_available(actor: User) -> None:
    if not actor.is_active or actor.deleted_at is not None:
        raise HTTPException(status_code=403, detail="User account is unavailable")


async def save_notifications_in_background(
    user_ids: list[UUID],
    category: NotificationCategory,
    title: str,
    message: str,
    event_id: UUID | None,
    booking_id: UUID | None,
) -> None:
    async with AsyncSessionLocal() as db:
        await NotificationRepository.create_for_users(
            user_ids, category, title, message, event_id, booking_id, db
        )
        await db.commit()


async def get_my_notifications(
    actor: User, filters: NotificationFilters, db: AsyncSession
) -> NotificationListResponse:
    _require_available(actor)
    authorize(actor, Action.notifications_view, owner_id=actor.id)
    notifications, total = await NotificationRepository.list_for_user(actor.id, filters, db)
    return NotificationListResponse(
        items=[NotificationResponse.model_validate(item) for item in notifications],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
    )


async def set_notification_read_state(
    actor: User, notification_id: UUID, payload: NotificationReadUpdate, db: AsyncSession
) -> NotificationResponse:
    _require_available(actor)
    notification = await NotificationRepository.get_notification_for_user_for_update(
        notification_id, actor.id, db
    )
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    authorize(actor, Action.notifications_update, owner_id=notification.user_id)

    if notification.is_read == payload.is_read:
        response = NotificationResponse.model_validate(notification)
        await db.commit()
        return response

    read_at = datetime.now(timezone.UTC) if payload.is_read else None
    try:
        notification = await NotificationRepository.set_read_state(
            notification, payload.is_read, read_at, db
        )
        response = NotificationResponse.model_validate(notification)
        await db.commit()
        return response
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Notification could not be updated") from None
