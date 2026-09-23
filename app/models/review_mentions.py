from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.reviews import Review
    from app.models.users import User


class ReviewMention(Base):
    __tablename__ = "review_mentions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentioned_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    review_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (
        UniqueConstraint("review_id", "mentioned_user_id", name="uq_review_user"),
    )

    mentioned_user: Mapped[User] = relationship(back_populates="review_mentions")
    review: Mapped[Review] = relationship(back_populates="mentions")