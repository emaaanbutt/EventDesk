from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import NotificationCategory, NotificationType


class NotificationResponse(BaseModel):
    id: UUID
    event_id: UUID | None
    booking_id: UUID | None
    review_id: UUID | None
    type: NotificationType
    title: str
    message: str
    is_read: bool
    created_at: datetime
    read_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class NotificationFilters(BaseModel):
    group: NotificationCategory | None = None
    type: NotificationType | None = None
    is_read: bool | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @model_validator(mode="after")
    def check_type_filter(self) -> "NotificationFilters":
        if self.group is not None and self.type is not None:
            raise ValueError("Choose either group or type")
        return self

    model_config = ConfigDict(extra="forbid")


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)


class NotificationReadUpdate(BaseModel):
    is_read: bool = Field(strict=True)

    model_config = ConfigDict(extra="forbid")
