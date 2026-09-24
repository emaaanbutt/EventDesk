from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CatalogItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip().casefold() if isinstance(value, str) else value

    model_config = ConfigDict(extra="forbid")


class CategoryResponse(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class TagResponse(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)
