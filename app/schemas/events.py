from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import EventStatus


def _strip_text(value: str | None) -> str | None:
    return value.strip() if isinstance(value, str) else value


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    venue: str = Field(min_length=1, max_length=255)
    starts_at: AwareDatetime
    ticket_price: Decimal = Field(ge=0, max_digits=10, decimal_places=2, allow_inf_nan=False)
    total_tickets: int = Field(gt=0)
    category_id: UUID | None = None
    tag_ids: list[UUID] = Field(default_factory=list)

    @field_validator("title", "description", "venue", mode="before")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return _strip_text(value)

    @field_validator("tag_ids")
    @classmethod
    def unique_tags(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("Tag IDs must be unique")
        return value

    model_config = ConfigDict(extra="forbid")


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    venue: str | None = Field(default=None, min_length=1, max_length=255)
    starts_at: AwareDatetime | None = None
    ticket_price: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2, allow_inf_nan=False
    )
    total_tickets: int | None = Field(default=None, gt=0)
    category_id: UUID | None = None
    tag_ids: list[UUID] | None = None

    @field_validator("title", "description", "venue", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return _strip_text(value)

    @field_validator("tag_ids")
    @classmethod
    def unique_tags(cls, value: list[UUID] | None) -> list[UUID] | None:
        if value is not None and len(value) != len(set(value)):
            raise ValueError("Tag IDs must be unique")
        return value

    @model_validator(mode="after")
    def require_changes(self) -> "EventUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")
        for field_name in self.model_fields_set - {"category_id"}:
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self

    model_config = ConfigDict(extra="forbid")


class CategoryResponse(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class TagResponse(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class EventResponse(BaseModel):
    id: UUID
    organizer_id: UUID
    category_id: UUID | None
    title: str
    description: str
    venue: str
    starts_at: datetime
    ticket_price: Decimal
    total_tickets: int
    status: EventStatus
    category: CategoryResponse | None
    tags: list[TagResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventListResponse(BaseModel):
    items: list[EventResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)


class EventFilters(BaseModel):
    search: str | None = Field(default=None, min_length=1, max_length=100)
    category_id: UUID | None = None
    tag_id: UUID | None = None
    date_from: AwareDatetime | None = None
    date_to: AwareDatetime | None = None
    sort: Literal["date_asc", "date_desc", "price_asc", "price_desc"] = "date_asc"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @field_validator("search", mode="before")
    @classmethod
    def strip_search(cls, value: str | None) -> str | None:
        return _strip_text(value)

    @model_validator(mode="after")
    def check_date_range(self) -> "EventFilters":
        if self.date_from is not None and self.date_to is not None and self.date_from > self.date_to:
            raise ValueError("date_from must be before or equal to date_to")
        return self

    model_config = ConfigDict(extra="forbid")
