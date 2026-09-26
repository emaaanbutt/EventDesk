from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.role_policy import Action
from app.models.enums import EventStatus, NotificationCategory
from app.models.events import Event
from app.models.tags import Tag
from app.models.users import User
from app.repositories.booking_repository import BookingRepository
from app.repositories.event_repository import EventRepository
from app.realtime.publisher import publish_event_availability
from app.schemas.events import EventCreate, EventFilters, EventListResponse, EventResponse, EventUpdate, EventAvailabilityResponse
from app.services import notification_service
from app.services.audit_log_service import record_audit_log
from app.services.authorization_service import authorize


def _require_available(actor: User) -> None:
    if not actor.is_active or actor.deleted_at is not None:
        raise HTTPException(status_code=403, detail="User account is unavailable")


async def _get_event_or_404(event_id: UUID, db: AsyncSession) -> Event:
    event = await EventRepository.get_by_id(event_id, db)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


async def _get_event_for_change_or_404(event_id: UUID, db: AsyncSession) -> Event:
    event = await EventRepository.get_by_id_for_update(event_id, db)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


async def _validate_category(category_id: UUID | None, db: AsyncSession) -> None:
    if category_id is not None and await EventRepository.get_category_by_id(category_id, db) is None:
        raise HTTPException(status_code=422, detail="Unknown category")


async def _get_valid_tags(tag_ids: list[UUID], db: AsyncSession) -> list[Tag]:
    tags = await EventRepository.get_tags_by_ids(tag_ids, db)
    if len(tags) != len(tag_ids):
        raise HTTPException(status_code=422, detail="Unknown tag")
    return tags


def _ensure_editable(event: Event) -> None:
    if event.status not in (EventStatus.draft, EventStatus.published):
        raise HTTPException(status_code=409, detail="This event cannot be edited")


def _ensure_publishable(event: Event) -> None:
    if event.status != EventStatus.draft:
        raise HTTPException(status_code=409, detail="Only a draft event can be published")
    if event.starts_at.tzinfo is None or event.starts_at.utcoffset() is None:
        raise HTTPException(status_code=409, detail="Event start time has no timezone")
    if event.starts_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=409, detail="Event start time must be in the future")


def _ensure_completable(event: Event) -> None:
    if event.status != EventStatus.published:
        raise HTTPException(status_code=409, detail="Only a published event can be completed")
    if event.ends_at.tzinfo is None or event.ends_at.utcoffset() is None:
        raise HTTPException(status_code=409, detail="Event end time has no timezone")
    if event.ends_at > datetime.now(timezone.utc):
        raise HTTPException(status_code=409, detail="Event has not ended yet")


def _ensure_cancellable(event: Event) -> None:
    if event.status not in (EventStatus.draft, EventStatus.published):
        raise HTTPException(status_code=409, detail="This event cannot be cancelled")


def _to_response(event: Event) -> EventResponse:
    return EventResponse.model_validate(event)


async def create_event(actor: User, payload: EventCreate, db: AsyncSession) -> EventResponse:
    _require_available(actor)
    authorize(actor, Action.events_create)
    if payload.starts_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=422, detail="Event start time must be in the future")

    await _validate_category(payload.category_id, db)
    tags = await _get_valid_tags(payload.tag_ids, db)
    values = payload.model_dump(exclude={"tag_ids"})

    try:
        event = await EventRepository.create_event(values, actor.id, EventStatus.draft, tags, db)
        await record_audit_log(actor.id, Action.events_create, "event", event.id, None, db)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Event could not be created because related data changed") from None
    return _to_response(event)


async def update_event(
    actor: User, event_id: UUID, payload: EventUpdate, db: AsyncSession,
    background_tasks: BackgroundTasks,
) -> EventResponse:
    _require_available(actor)
    event = await _get_event_for_change_or_404(event_id, db)
    authorize(actor, Action.events_edit, owner_id=event.organizer_id)
    _ensure_editable(event)

    changes = payload.model_dump(exclude_unset=True, exclude={"tag_ids"})
    if "starts_at" in changes and changes["starts_at"] <= datetime.now(timezone.utc):
        raise HTTPException(status_code=422, detail="Event start time must be in the future")
    new_start = changes.get("starts_at", event.starts_at)
    new_end = changes.get("ends_at", event.ends_at)
    if new_end <= new_start:
        raise HTTPException(status_code=422, detail="Event end time must be after start time")
    if "total_tickets" in changes:
        booked_tickets = await BookingRepository.get_confirmed_ticket_count(event.id, db)
        if changes["total_tickets"] < booked_tickets:
            raise HTTPException(status_code=409, detail="Total tickets cannot be less than tickets already booked")
    if "category_id" in changes:
        await _validate_category(changes["category_id"], db)
    tags = None
    if "tag_ids" in payload.model_fields_set:
        if payload.tag_ids is None:
            raise HTTPException(status_code=422, detail="tag_ids cannot be null")
        tags = await _get_valid_tags(payload.tag_ids, db)

    try:
        event = await EventRepository.update_event(event, changes, tags, db)
        changed_fields = list(changes)
        if tags is not None:
            changed_fields.append("tag_ids")
        if changed_fields:
            await record_audit_log(
                actor.id, Action.events_edit, "event", event.id,
                {"fields": sorted(changed_fields)}, db,
            )
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Event could not be updated because related data changed") from None
    if "total_tickets" in changes and event.status == EventStatus.published:
        background_tasks.add_task(publish_event_availability, event.id)
    return _to_response(event)


async def publish_event(actor: User, event_id: UUID, db: AsyncSession) -> EventResponse:
    _require_available(actor)
    event = await _get_event_for_change_or_404(event_id, db)
    authorize(actor, Action.events_publish, owner_id=event.organizer_id)
    _ensure_publishable(event)

    try:
        await EventRepository.set_status(event, EventStatus.published, db)
        await record_audit_log(actor.id, Action.events_publish, "event", event.id, None, db)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Event could not be published") from None
    return _to_response(event)


async def complete_event(actor: User, event_id: UUID, db: AsyncSession) -> EventResponse:
    _require_available(actor)
    event = await _get_event_for_change_or_404(event_id, db)
    authorize(actor, Action.events_complete, owner_id=event.organizer_id)
    _ensure_completable(event)

    try:
        await EventRepository.set_status(event, EventStatus.completed, db)
        await record_audit_log(actor.id, Action.events_complete, "event", event.id, None, db)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Event could not be completed") from None
    return _to_response(event)


async def complete_due_events(db: AsyncSession) -> int:
    event_ids = await EventRepository.mark_due_events_completed(datetime.now(timezone.utc), db)
    for event_id in event_ids:
        await record_audit_log(
            None, Action.events_complete, "event", event_id, {"source": "scheduler"}, db
        )
    await db.commit()
    return len(event_ids)


async def cancel_event(
    actor: User, event_id: UUID, db: AsyncSession, background_tasks: BackgroundTasks
) -> EventResponse:
    _require_available(actor)
    event = await _get_event_for_change_or_404(event_id, db)
    authorize(actor, Action.events_cancel, owner_id=event.organizer_id)
    _ensure_cancellable(event)

    try:
        attendee_ids = await BookingRepository.get_confirmed_attendee_ids(event.id, db)
        await EventRepository.set_status(event, EventStatus.cancelled, db)
        await record_audit_log(actor.id, Action.events_cancel, "event", event.id, None, db)
        response = _to_response(event)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Event could not be cancelled") from None
    background_tasks.add_task(publish_event_availability, event.id)
    if attendee_ids:
        background_tasks.add_task(
            notification_service.save_notifications_in_background,
            user_ids=attendee_ids,
            category=NotificationCategory.event,
            title="Event cancelled",
            message=f"{event.title} has been cancelled.",
            event_id=event.id,
            booking_id=None,
            review_id=None
        )
    return response


async def list_published_events(filters: EventFilters, db: AsyncSession) -> EventListResponse:
    events, total = await EventRepository.list_published(filters, db)
    return EventListResponse(
        items=[_to_response(event) for event in events],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
    )


async def get_published_event(event_id: UUID, db: AsyncSession) -> EventResponse:
    event = await _get_event_or_404(event_id, db)
    if event.status != EventStatus.published:
        raise HTTPException(status_code=404, detail="Event not found")
    return _to_response(event)


async def get_my_events(actor: User, db: AsyncSession) -> list[EventResponse]:
    _require_available(actor)
    authorize(actor, Action.events_view_own)
    events = await EventRepository.list_by_organizer(actor.id, db)
    return [_to_response(event) for event in events]


async def get_managed_event(actor: User, event_id: UUID, db: AsyncSession) -> EventResponse:
    _require_available(actor)
    event = await _get_event_or_404(event_id, db)
    authorize(actor, Action.events_edit, owner_id=event.organizer_id)
    return _to_response(event)


async def get_event_availability(event_id: UUID, db: AsyncSession) -> EventAvailabilityResponse:
    event = await _get_event_or_404(event_id, db)
    if event.status != EventStatus.published:
        raise HTTPException(status_code=404, detail="Event not found")
    total_seats = event.total_tickets
    booked_seats = await BookingRepository.get_confirmed_ticket_count(event_id, db)

    available_seats = total_seats - booked_seats
    return EventAvailabilityResponse(
        event_id=event_id,
        total_tickets=total_seats,
        booked_tickets=booked_seats,
        remaining_tickets=available_seats,
    )
