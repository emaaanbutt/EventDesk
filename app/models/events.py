from sqlalchemy import Integer, String, VARCHAR, Enum, Boolean, Text, DateTime, Decimal
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base, TimeStamp
from enums import EventStatus
from datetime import datetime

class Event(Base, TimeStamp):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey(), nullable=True)
    title: Mapped[str] = mapped_column(VARCHAR(255))
    description: Mapped[str] = mapped_column(Text, unique=True)
    venue: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ticket_price: Mapped[float] = mapped_column(Decimal(10,2), nullable=False)
    total_tickets: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus, name="status"), nullable=False)
    organizer_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)
