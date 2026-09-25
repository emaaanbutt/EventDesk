from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.role_policy import Action
from app.models.enums import BookingStatus, EventStatus, NotificationCategory
from app.models.users import User
from app.repositories.booking_repository import BookingRepository
from app.repositories.event_repository import EventRepository
from app.schemas.bookings import BookingCreate, BookingFilters, BookingListResponse, BookingResponse
from app.services import notification_service
from app.services.authorization_service import authorize


def _require_available(actor: User) -> None:
    if not actor.is_active or actor.deleted_at is not None:
        raise HTTPException(status_code=403, detail="User account is unavailable")


async def create_booking(
    actor: User, payload: BookingCreate, db: AsyncSession, background_tasks: BackgroundTasks
) -> BookingResponse:
    _require_available(actor)
    authorize(actor, Action.bookings_create)

    try:
        event = await EventRepository.get_by_id_for_update(payload.event_id, db)
        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")
        if event.status != EventStatus.published:
            raise HTTPException(status_code=409, detail="Only published events can be booked")
        if event.starts_at <= datetime.now(timezone.UTC):
            raise HTTPException(status_code=409, detail="Booking is closed for this event")

        booked_tickets = await BookingRepository.get_confirmed_ticket_count(event.id, db)
        available_tickets = event.total_tickets - booked_tickets
        if payload.quantity > available_tickets:
            raise HTTPException(status_code=409, detail="Not enough tickets available")

        total_amount = event.ticket_price * payload.quantity
        if total_amount > Decimal("99999999.99"):
            raise HTTPException(status_code=422, detail="Booking total exceeds the supported amount")

        booking = await BookingRepository.create_booking(
            event.id, actor.id, payload.quantity, total_amount, db
        )
        response = BookingResponse.model_validate(booking)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Booking could not be completed") from None
    except Exception:
        await db.rollback()
        raise
    background_tasks.add_task(
        notification_service.save_notifications_in_background,
        user_ids=[actor.id],
        category=NotificationCategory.booking,
        title="Booking confirmed",
        message=f"Your booking for {event.title} is confirmed.",
        event_id=event.id,
        booking_id=booking.id,
    )
    return response


async def cancel_booking(
    actor: User, booking_id: UUID, db: AsyncSession, background_tasks: BackgroundTasks
) -> BookingResponse:
    _require_available(actor)

    try:
        event_id = await BookingRepository.get_event_id(booking_id, db)
        if event_id is None:
            raise HTTPException(status_code=404, detail="Booking not found")

        event = await EventRepository.get_by_id_for_update(event_id, db)
        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")
        booking = await BookingRepository.get_by_id_for_update(booking_id, db)
        if booking is None or booking.event_id != event.id:
            raise HTTPException(status_code=404, detail="Booking not found")
        authorize(actor, Action.bookings_cancel, owner_id=booking.attendee_id)
        if booking.status == BookingStatus.cancelled:
            raise HTTPException(status_code=409, detail="Booking is already cancelled")

        booking = await BookingRepository.cancel_booking(booking, db)
        response = BookingResponse.model_validate(booking)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Booking could not be cancelled") from None
    except Exception:
        await db.rollback()
        raise
    background_tasks.add_task(
        notification_service.save_notifications_in_background,
        user_ids=[booking.attendee_id],
        category=NotificationCategory.booking,
        title="Booking cancelled",
        message=f"Your booking for {event.title} has been cancelled.",
        event_id=event.id,
        booking_id=booking.id,
    )
    return response


async def get_my_bookings(
    actor: User, filters: BookingFilters, db: AsyncSession
) -> BookingListResponse:
    _require_available(actor)
    authorize(actor, Action.bookings_view, owner_id=actor.id)
    bookings, total = await BookingRepository.list_bookings_for_user(
        actor.id, filters.page, filters.page_size, db
    )
    return BookingListResponse(
        items=[BookingResponse.model_validate(booking) for booking in bookings],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
    )


async def get_all_bookings(
    actor: User, filters: BookingFilters, db: AsyncSession
) -> BookingListResponse:
    _require_available(actor)
    authorize(actor, Action.bookings_view)
    bookings, total = await BookingRepository.list_all_bookings(
        filters.page, filters.page_size, db
    )
    return BookingListResponse(
        items=[BookingResponse.model_validate(booking) for booking in bookings],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
    )
