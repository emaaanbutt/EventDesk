from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bookings import Booking
from app.models.enums import BookingStatus


class BookingRepository:
    @staticmethod
    async def get_confirmed_ticket_count(event_id: UUID, db: AsyncSession) -> int:
        result = await db.execute(
            select(func.coalesce(func.sum(Booking.quantity), 0)).where(
                Booking.event_id == event_id,
                Booking.status == BookingStatus.confirmed,
                Booking.deleted_at.is_(None),
            )
        )
        return result.scalar_one()

    @staticmethod
    async def get_confirmed_attendee_ids(event_id: UUID, db: AsyncSession) -> list[UUID]:
        result = await db.execute(
            select(Booking.attendee_id)
            .where(
                Booking.event_id == event_id,
                Booking.status == BookingStatus.confirmed,
                Booking.deleted_at.is_(None),
            )
            .distinct()
        )
        return list(result.scalars().all())
