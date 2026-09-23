from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Text, UUID, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimeStamp
from app.models.enums import NotificationType

if TYPE_CHECKING:
    from app.models.bookings import Booking
    from app.models.events import Event
    from app.models.reviews import Review
    from app.models.users import User


class Notification(Base, TimeStamp):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=True)
    booking_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), nullable=True)
    type: Mapped[NotificationType] = mapped_column("type", Enum(NotificationType, name="notification_type"), nullable=False)
    title: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    review_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), nullable=True)

    user: Mapped[User] = relationship(back_populates="notifications")
    event: Mapped[Event | None] = relationship(back_populates="notifications")
    booking: Mapped[Booking | None] = relationship(back_populates="notifications")
    review: Mapped[Review | None] = relationship(back_populates="notifications")