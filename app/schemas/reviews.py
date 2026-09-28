from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _strip_comment(value: str | None) -> str | None:
    return value.strip() if isinstance(value, str) else value


class ReviewCreate(BaseModel):
    event_id: UUID
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=1, max_length=500)

    @field_validator("comment", mode="before")
    @classmethod
    def strip_comment(cls, value: str) -> str:
        return _strip_comment(value)

    model_config = ConfigDict(extra="forbid")


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = Field(default=None, min_length=1, max_length=500)

    @field_validator("comment", mode="before")
    @classmethod
    def strip_comment(cls, value: str | None) -> str | None:
        return _strip_comment(value)

    @model_validator(mode="after")
    def require_changes(self) -> "ReviewUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")
        for field_name in self.model_fields_set:
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self

    model_config = ConfigDict(extra="forbid")


class ReviewResponse(BaseModel):
    id: UUID
    event_id: UUID
    author_id: UUID
    rating: int
    comment: str
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ReviewListResponse(BaseModel):
    items: list[ReviewResponse]
    total: int = Field(ge=0)
    page: int = Field(ge=1, default=1)
    page_size: int = Field(ge=1, le=100, default=20)
