from sqlalchemy import Integer, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base, TimeStamp
from enums import WaitlistEntryStatus

class WaitlistEntry(Base, TimeStamp):
    __tablename__ = "waitlist_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    position: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[WaitlistEntryStatus] = mapped_column(Enum(WaitlistEntryStatus, name="status"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "event_id", name="uq_event_user"))
   