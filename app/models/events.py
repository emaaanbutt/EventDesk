from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, Text, UUID, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimeStamp
from app.models.enums import EventStatus

if TYPE_CHECKING:
    from app.models.bookings import Booking
    from app.models.categories import Category
    from app.models.event_tags import EventTag
    from app.models.notifications import Notification
    from app.models.tags import Tag
    from app.models.users import User
    from app.models.reviews import Review


class Event(Base, TimeStamp):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    venue: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ticket_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_tickets: Mapped[int] = mapped_column(Integer, nullable=False)
<<<<<<< HEAD
    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus, name="status"), nullable=False)
=======
    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus, name="event_status"), nullable=False)
>>>>>>> 2c7340c25a1fe87c4e3accab185997b8bdb3cd5e
    organizer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    category: Mapped[Category] = relationship(back_populates="events")
    organizer: Mapped[User] = relationship(back_populates="events")
    bookings: Mapped[list[Booking]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list[Review]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list[Notification]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
    )
    event_tags: Mapped[list[EventTag]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
        overlaps="tags",
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary="event_tags",
        back_populates="events",
        overlaps="event_tags,event,tag",
    )

