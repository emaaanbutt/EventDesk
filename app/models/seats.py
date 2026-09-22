from sqlalchemy import UniqueConstraint, DateTime, Enum, func, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base
from enums import EventFrequency
from datetime import datetime


class RecurrenceRule(Base):
    __tablename__ = "recurrence_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)
    section: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    row_label: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    seat_number: Mapped[str] = mapped_column(VARCHAR, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
                DateTime(timezone=True), nullable=False, server_default=func.now()
            )

    __table_args__ = (UniqueConstraint("event_id", "section","row_label", "seat_number", name="uq_seat"))
    

   