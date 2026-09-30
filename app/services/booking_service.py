from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import BackgroundTasks
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    InvalidInputError,
    NotFoundError,
    PermissionDeniedError,
)
from app.core.role_policy import Action
from app.models.enums import BookingStatus, EventStatus, NotificationCategory
from app.models.users import User
from app.repositories.booking_repository import BookingRepository
from app.repositories.event_repository import EventRepository
from app.realtime.publisher import publish_event_availability
from app.schemas.bookings import BookingCreate, BookingFilters, BookingListResponse, BookingResponse
from app.services import notification_service
from app.services.audit_log_service import record_audit_log
from app.services.authorization_service import authorize_db


def _require_available(actor: User) -> None:
    if not actor.is_active or actor.deleted_at is not None:
        raise PermissionDeniedError(detail="User account is unavailable")


async def create_booking(
    actor: User, payload: BookingCreate, db: AsyncSession, background_tasks: BackgroundTasks
) -> BookingResponse:
    _require_available(actor)
    await authorize_db(actor, Action.bookings_create, db)

    try:
        event = await EventRepository.get_by_id_for_update(payload.event_id, db)
        if event is None:
            raise NotFoundError(detail="Event not found")
        if event.organizer_id == actor.id:
            raise PermissionDeniedError(detail="You cannot book your own event")
        if event.status != EventStatus.published:
            raise ConflictError(detail="Only published events can be booked")
        if event.starts_at <= datetime.now(timezone.utc):
            raise ConflictError(detail="Booking is closed for this event")

        booked_tickets = await BookingRepository.get_confirmed_ticket_count(event.id, db)
        available_tickets = event.total_tickets - booked_tickets
        if payload.quantity > available_tickets:
            raise ConflictError(detail="Not enough tickets available")

        total_amount = event.ticket_price * payload.quantity
        if total_amount > Decimal("99999999.99"):
            raise InvalidInputError(detail="Booking total exceeds the supported amount")

        booking = await BookingRepository.create_booking(
            event.id, actor.id, payload.quantity, total_amount, db
        )
        response = BookingResponse.model_validate(booking)
        await record_audit_log(
            actor.id,
            Action.bookings_create,
            "booking",
            booking.id,
            {"event_id": str(event.id), "quantity": booking.quantity},
            db,
        )
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictError(detail="Booking could not be completed") from None
    background_tasks.add_task(publish_event_availability, event.id)
    background_tasks.add_task(
        notification_service.save_notifications_in_background,
        user_ids=[actor.id],
        category=NotificationCategory.booking,
        title="Booking confirmed",
        message=f"Your booking for {event.title} is confirmed.",
        event_id=event.id,
        booking_id=booking.id,
        review_id=None,
    )
    return response


async def cancel_booking(
    actor: User, booking_id: UUID, db: AsyncSession, background_tasks: BackgroundTasks
) -> BookingResponse:
    _require_available(actor)

    try:
        event_id = await BookingRepository.get_event_id(booking_id, db)
        if event_id is None:
            raise NotFoundError(detail="Booking not found")

        event = await EventRepository.get_by_id_for_update(event_id, db)
        if event is None:
            raise NotFoundError(detail="Event not found")
        booking = await BookingRepository.get_by_id_for_update(booking_id, db)
        if booking is None or booking.event_id != event.id:
            raise NotFoundError(detail="Booking not found")
        await authorize_db(actor, Action.bookings_cancel, db, owner_id=booking.attendee_id)
        if booking.status == BookingStatus.cancelled:
            raise ConflictError(detail="Booking is already cancelled")

        booking = await BookingRepository.cancel_booking(booking, db)
        response = BookingResponse.model_validate(booking)
        await record_audit_log(
            actor.id,
            Action.bookings_cancel,
            "booking",
            booking.id,
            {"event_id": str(event.id), "quantity": booking.quantity},
            db,
        )
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictError(detail="Booking could not be cancelled") from None
    background_tasks.add_task(publish_event_availability, event.id)
    background_tasks.add_task(
        notification_service.save_notifications_in_background,
        user_ids=[booking.attendee_id],
        category=NotificationCategory.booking,
        title="Booking cancelled",
        message=f"Your booking for {event.title} has been cancelled.",
        event_id=event.id,
        booking_id=booking.id,
        review_id=None,
    )
    return response


async def delete_booking(
    actor: User, booking_id: UUID, db: AsyncSession, background_tasks: BackgroundTasks
) -> None:
    _require_available(actor)
    try:
        event_id = await BookingRepository.get_event_id(booking_id, db)
        if event_id is None:
            raise NotFoundError(detail="Booking not found")
        event = await EventRepository.get_by_id_for_update(event_id, db, include_deleted=True)
        if event is None:
            raise NotFoundError(detail="Event not found")
        booking = await BookingRepository.get_by_id_for_update(booking_id, db)
        if booking is None or booking.event_id != event.id:
            raise NotFoundError(detail="Booking not found")
        await authorize_db(actor, Action.bookings_delete, db, owner_id=booking.attendee_id)
        was_confirmed = booking.status == BookingStatus.confirmed
        if was_confirmed:
            await BookingRepository.cancel_booking(booking, db)
        await BookingRepository.soft_delete(booking, db)
        await record_audit_log(
            actor.id,
            Action.bookings_delete,
            "booking",
            booking.id,
            {"event_id": str(event.id), "quantity": booking.quantity},
            db,
        )
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictError(detail="Booking could not be deleted") from None
    if was_confirmed:
        background_tasks.add_task(publish_event_availability, event.id)
        background_tasks.add_task(
            notification_service.save_notifications_in_background,
            user_ids=[booking.attendee_id],
            category=NotificationCategory.booking,
            title="Booking cancelled",
            message=f"Your booking for {event.title} was cancelled.",
            event_id=event.id,
            booking_id=booking.id,
            review_id=None,
        )


async def get_my_bookings(
    actor: User, filters: BookingFilters, db: AsyncSession
) -> BookingListResponse:
    _require_available(actor)
    await authorize_db(actor, Action.bookings_view, db, owner_id=actor.id)
    bookings, total = await BookingRepository.list_bookings_for_user(
        actor.id, filters.page, filters.page_size, db
    )
    return BookingListResponse(
        items=[
            BookingResponse.model_validate(booking).model_copy(
                update={
                    "event_title": booking.event.title,
                    "event_status": booking.event.status,
                    "event_deleted": booking.event.deleted_at is not None,
                }
            )
            for booking in bookings
        ],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
    )


async def get_all_bookings(
    actor: User, filters: BookingFilters, db: AsyncSession
) -> BookingListResponse:
    _require_available(actor)
    await authorize_db(actor, Action.bookings_view, db)
    bookings, total = await BookingRepository.list_all_bookings(filters.page, filters.page_size, db)
    return BookingListResponse(
        items=[
            BookingResponse.model_validate(booking).model_copy(
                update={
                    "event_title": booking.event.title,
                    "event_status": booking.event.status,
                    "event_deleted": booking.event.deleted_at is not None,
                    "attendee_name": booking.attendee.name,
                }
            )
            for booking in bookings
        ],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
    )
