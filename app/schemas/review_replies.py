from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReviewReplyCreate(BaseModel):
    comment: str = Field(min_length=1, max_length=500)

    @field_validator("comment", mode="before")
    @classmethod
    def strip_comment(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    model_config = ConfigDict(extra="forbid")


class ReviewReplyResponse(BaseModel):
    id: UUID
    review_id: UUID
    author_id: UUID
    comment: str
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
