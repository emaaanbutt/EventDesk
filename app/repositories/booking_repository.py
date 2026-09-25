from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
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

    @staticmethod
    async def create_booking(
        event_id: UUID,
        attendee_id: UUID,
        quantity: int,
        total_amount: Decimal,
        db: AsyncSession,
    ) -> Booking:
        booking = Booking(
            event_id=event_id,
            attendee_id=attendee_id,
            quantity=quantity,
            total_amount=total_amount,
            status=BookingStatus.confirmed,
            booked_at=datetime.now(timezone.utc),
        )
        db.add(booking)
        await db.flush()
        await db.refresh(booking)
        return booking

    @staticmethod
    async def get_event_id(booking_id: UUID, db: AsyncSession) -> UUID | None:
        result = await db.execute(
            select(Booking.event_id).where(
                Booking.id == booking_id, Booking.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id_for_update(booking_id: UUID, db: AsyncSession) -> Booking | None:
        result = await db.execute(
            select(Booking)
            .where(Booking.id == booking_id, Booking.deleted_at.is_(None))
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def cancel_booking(booking: Booking, db: AsyncSession) -> Booking:
        booking.status = BookingStatus.cancelled
        booking.cancelled_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(booking, attribute_names=["updated_at"])
        return booking

    @staticmethod
    async def list_bookings_for_user(
        user_id: UUID, page: int, page_size: int, db: AsyncSession
    ) -> tuple[list[Booking], int]:
        conditions = (Booking.attendee_id == user_id, Booking.deleted_at.is_(None))
        count_result = await db.execute(select(func.count(Booking.id)).where(*conditions))
        result = await db.execute(
            select(Booking)
            .where(*conditions)
            .order_by(Booking.booked_at.desc(), Booking.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), count_result.scalar_one()

    @staticmethod
    async def has_confirmed_booking(event_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
        result = await db.execute(
            select(Booking.id)
            .where(
                Booking.event_id == event_id,
                Booking.attendee_id == user_id,
                Booking.deleted_at.is_(None),
                Booking.status == BookingStatus.confirmed,
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None
