from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BookingStatus


class BookingCreate(BaseModel):
    event_id: UUID
    quantity: int = Field(gt=0)

    model_config = ConfigDict(extra="forbid")


class BookingResponse(BaseModel):
    id: UUID
    event_id: UUID
    attendee_id: UUID
    quantity: int
    total_amount: Decimal
    status: BookingStatus
    booked_at: datetime
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BookingFilters(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    model_config = ConfigDict(extra="forbid")

class BookingListResponse(BaseModel):
    items: list[BookingResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)

    model_config = ConfigDict(extra="forbid")
