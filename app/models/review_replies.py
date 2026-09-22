from sqlalchemy import Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base, TimeStamp


class ReviewReply(Base, TimeStamp):
    __tablename__ = "review_replies"

    id: Mapped[int] = mapped_column(primary_key=True)
    auther_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)
    review_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False, unique=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
   