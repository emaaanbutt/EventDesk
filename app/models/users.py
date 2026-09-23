from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, UUID, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimeStamp
from app.models.enums import Role
from app.models.refresh_tokens import RefreshToken

if TYPE_CHECKING:
    from app.models.audit_logs import AuditLog
    from app.models.bookings import Booking
    from app.models.events import Event
    from app.models.notifications import Notification
    from app.models.refresh_tokens import RefreshToken
    from app.models.review_mentions import ReviewMention
    from app.models.reviews import Review


class User(Base, TimeStamp):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(VARCHAR(100), nullable=False)
    email: Mapped[str] = mapped_column(VARCHAR(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role, name="role"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    events: Mapped[list[Event]] = relationship(
        back_populates="organizer",
        cascade="all, delete-orphan",
    )
    bookings: Mapped[list[Booking]] = relationship(
        back_populates="attendee",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list[Review]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list[Notification]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(
        back_populates="actor",
        cascade="all, delete-orphan",
    )
    review_mentions: Mapped[list[ReviewMention]] = relationship(
        back_populates="mentioned_user",
        cascade="all, delete-orphan",
    )
