from sqlalchemy import  UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base


class ReviewMention(Base):
    __tablename__ = "review_mentions"

    id: Mapped[int] = mapped_column(primary_key=True)
    mentioned_user_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)
    review_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)

    __table_args__ = (
        UniqueConstraint("review_id", "mentioned_user_id", name="uq_review_user")
    )
    