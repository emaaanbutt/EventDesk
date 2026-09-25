from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import NotificationCategory
from app.models.notifications import Notification
from app.schemas.notifications import NotificationFilters


class NotificationRepository:
    @staticmethod
    async def list_for_user(
        user_id: UUID, filters: NotificationFilters, db: AsyncSession
    ) -> tuple[list[Notification], int]:
        conditions = [Notification.user_id == user_id, Notification.deleted_at.is_(None)]

        if filters.is_read is not None:
            conditions.append(Notification.is_read == filters.is_read)
        if filters.type is not None:
            conditions.append(Notification.type == filters.type)

        count_result = await db.execute(select(func.count(Notification.id)).where(*conditions))
        result = await db.execute(
            select(Notification)
            .where(*conditions)
            .order_by(Notification.created_at.desc(), Notification.id.asc())
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        return list(result.scalars().all()), count_result.scalar_one()

    @staticmethod
    async def create_for_users(
        user_ids: list[UUID],
        category: NotificationCategory,
        title: str,
        message: str,
        event_id: UUID | None,
        booking_id: UUID | None,
        review_id: UUID| None,
        db: AsyncSession,
    ) -> None:
        notifications = [
            Notification(
                user_id=user_id,
                event_id=event_id,
                booking_id=booking_id,
                review_id=review_id,
                type=category,
                title=title,
                message=message,
                is_read=False,
            )
            for user_id in user_ids
        ]
        if notifications:
            db.add_all(notifications)
            await db.flush()

    @staticmethod
    async def get_notification_for_user_for_update(
        notification_id: UUID, user_id: UUID, db: AsyncSession
    ) -> Notification | None:
        result = await db.execute(
            select(Notification)
            .where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
                Notification.deleted_at.is_(None),
            )
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def set_read_state(
        notification: Notification, is_read: bool, read_at: datetime | None, db: AsyncSession
    ) -> Notification:
        notification.is_read = is_read
        notification.read_at = read_at
        await db.flush()
        return notification
