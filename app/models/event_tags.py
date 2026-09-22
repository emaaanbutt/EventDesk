from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.events import Event
    from app.models.tags import Tag


class EventTag(Base):
    __tablename__ = "event_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (UniqueConstraint("event_id", "tag_id", name="uq_event_tag"),)

    event: Mapped["Event"] = relationship(back_populates="event_tags")
    tag: Mapped["Tag"] = relationship(back_populates="event_tags")

   