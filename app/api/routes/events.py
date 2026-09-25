from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.users import User
from app.schemas.events import EventCreate, EventFilters, EventListResponse, EventResponse, EventUpdate
from app.services import event_service

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    return await event_service.create_event(actor, payload, db)


@router.get("/", response_model=EventListResponse)
async def list_published_events(
    filters: Annotated[EventFilters, Query()],
    db: AsyncSession = Depends(get_db),
) -> EventListResponse:
    return await event_service.list_published_events(filters, db)


@router.get("/mine", response_model=list[EventResponse])
async def get_my_events(
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[EventResponse]:
    return await event_service.get_my_events(actor, db)


@router.get("/{event_id}", response_model=EventResponse)
async def get_published_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    return await event_service.get_published_event(event_id, db)


@router.get("/{event_id}/manage", response_model=EventResponse)
async def get_managed_event(
    event_id: UUID,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    return await event_service.get_managed_event(actor, event_id, db)


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,
    payload: EventUpdate,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    return await event_service.update_event(actor, event_id, payload, db)


@router.post("/{event_id}/publish", response_model=EventResponse)
async def publish_event(
    event_id: UUID,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    return await event_service.publish_event(actor, event_id, db)


@router.post("/{event_id}/complete", response_model=EventResponse)
async def complete_event(
    event_id: UUID,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    return await event_service.complete_event(actor, event_id, db)


@router.post("/{event_id}/cancel", response_model=EventResponse)
async def cancel_event(
    event_id: UUID,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    return await event_service.cancel_event(actor, event_id, db)
