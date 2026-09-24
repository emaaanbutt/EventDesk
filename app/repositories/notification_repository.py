from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import NotificationType
from app.models.events import Event
from app.models.notifications import Notification


class NotificationRepository:
    @staticmethod
    async def list_for_user(user_id: UUID, db: AsyncSession) -> list[Notification]:
        result = await db.execute(
            select(Notification)
            .where(Notification.user_id == user_id, Notification.deleted_at.is_(None))
            .order_by(Notification.created_at.desc(), Notification.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def create_event_cancellation_notifications(
        event: Event, attendee_ids: list[UUID], db: AsyncSession
    ) -> None:
        notifications = [
            Notification(
                event_id=event.id,
                user_id=attendee_id,
                type=NotificationType.event_cancelled,
                title="Event cancelled",
                message=f"{event.title} has been cancelled.",
                is_read=False,
            )
            for attendee_id in attendee_ids
        ]
        if notifications:
            db.add_all(notifications)
            await db.flush()
