from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.users import User
from app.schemas.bookings import BookingCreate, BookingFilters, BookingListResponse, BookingResponse
from app.services import booking_service

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreate,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    return await booking_service.create_booking(actor, payload, db)

@router.get("/me", response_model=BookingListResponse)
async def get_my_bookings(
    filters: Annotated[BookingFilters, Query()],
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookingListResponse:
    return await booking_service.get_my_bookings(actor, filters, db)


@router.get("", response_model=BookingListResponse)
async def get_all_bookings(
    filters: Annotated[BookingFilters, Query()],
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookingListResponse:
    return await booking_service.get_all_bookings(actor, filters, db)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: UUID,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    return await booking_service.cancel_booking(actor, booking_id, db)
