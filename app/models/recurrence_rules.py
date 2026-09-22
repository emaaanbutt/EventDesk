from sqlalchemy import UniqueConstraint, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base
from enums import EventFrequency
from datetime import datetime


class RecurrenceRule(Base):
    __tablename__ = "recurrence_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)
    frequency: Mapped[EventFrequency] = mapped_column(Enum(EventFrequency, name="status"), nullable=False)
    interval: Mapped[int] = mapped_column(default=1)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
                DateTime(timezone=True), nullable=False, server_default=func.now()
            )
    

   