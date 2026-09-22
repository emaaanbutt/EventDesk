from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, SMALLINT, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimeStamp

if TYPE_CHECKING:
    from app.models.notifications import Notification
    from app.models.review_mentions import ReviewMention
    from app.models.users import User
    from app.models.events import Event


class Review(Base, TimeStamp):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    rating: Mapped[int] = mapped_column(SMALLINT, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("author_id", "event_id", name="uq_event_author"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    author: Mapped["User"] = relationship(back_populates="reviews")
    event: Mapped["Event"] = relationship(back_populates="reviews")
    mentions: Mapped[list["ReviewMention"]] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
    )
   