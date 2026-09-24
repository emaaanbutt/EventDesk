from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.role_policy import Action
from app.models.enums import BookingStatus
from app.models.bookings import Booking
from app.models.users import User
from app.repositories.booking_repository import BookingRepository
from app.repositories.notification_repository import NotificationRepository
from app.schemas.bookings import BookingStatus, BookingResponse, BookingCreate, BookingFilters, BookingListResponse
from app.services.authorization_service import authorize


