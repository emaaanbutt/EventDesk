from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status

from app.core.dependencies import CurrentUser, DbSession, get_current_user, get_db
from app.schemas.bookings import BookingCreate, BookingFilters, BookingListResponse, BookingResponse
from app.services import booking_service

router = APIRouter(
    prefix="/bookings", tags=["bookings"], dependencies=[Depends(get_db), Depends(get_current_user)]
)


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreate,
    background_tasks: BackgroundTasks,
    actor: CurrentUser,
    db: DbSession,
) -> BookingResponse:
    return await booking_service.create_booking(actor, payload, db, background_tasks)


@router.get("/me", response_model=BookingListResponse)
async def get_my_bookings(
    filters: Annotated[BookingFilters, Query()],
    actor: CurrentUser,
    db: DbSession,
) -> BookingListResponse:
    return await booking_service.get_my_bookings(actor, filters, db)


@router.get("", response_model=BookingListResponse)
async def get_all_bookings(
    filters: Annotated[BookingFilters, Query()],
    actor: CurrentUser,
    db: DbSession,
) -> BookingListResponse:
    return await booking_service.get_all_bookings(actor, filters, db)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: UUID,
    background_tasks: BackgroundTasks,
    actor: CurrentUser,
    db: DbSession,
) -> BookingResponse:
    return await booking_service.cancel_booking(actor, booking_id, db, background_tasks)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: UUID,
    background_tasks: BackgroundTasks,
    actor: CurrentUser,
    db: DbSession,
) -> None:
    await booking_service.delete_booking(actor, booking_id, db, background_tasks)
