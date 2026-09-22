from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.reviews import Review
    from app.models.users import User


class ReviewMention(Base):
    __tablename__ = "review_mentions"

    id: Mapped[int] = mapped_column(primary_key=True)
    mentioned_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("review_id", "mentioned_user_id", name="uq_review_user"),
    )

    mentioned_user: Mapped["User"] = relationship(back_populates="review_mentions")
    review: Mapped["Review"] = relationship(back_populates="mentions")