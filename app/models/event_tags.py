from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base, TimeStamp


class EventTag(Base):
    __tablename__ = "event_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)
    tag_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)

    __table_args__ = (UniqueConstraint("event_id", "tag_id", name="uq_event_tag"))

   