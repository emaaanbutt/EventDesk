from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimeStamp

if TYPE_CHECKING:
    from app.models.event_tags import EventTag
    from app.models.events import Event


class Tag(Base, TimeStamp):
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(VARCHAR(255), unique=True, nullable=False)

    event_tags: Mapped[list[EventTag]] = relationship(
        back_populates="tag",
        cascade="all, delete-orphan",
        overlaps="events",
    )
    events: Mapped[list[Event]] = relationship(
        secondary="event_tags",
        back_populates="tags",
        overlaps="event_tags,event,tag",
    )
   