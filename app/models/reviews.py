from sqlalchemy import Text, UniqueConstraint, SMALLINT, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base, TimeStamp

class Review(Base, TimeStamp):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    auther_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)
    rating: Mapped[int] = mapped_column(SMALLINT)
    comment: Mapped[str] = mapped_column(Text)

    __table_args__ = (UniqueConstraint("author_id", "event_id", name="uq_event_author"),
                      CheckConstraint("(rating>=1) & (rating)<=5", name="check_rating_range"))
   