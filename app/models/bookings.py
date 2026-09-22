from sqlalchemy import Integer, String, VARCHAR, Enum, Boolean, Text, DateTime, Decimal
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base, TimeStamp
from enums import BookingStatus
from datetime import datetime

class Booking(Base, TimeStamp):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total_amount: Mapped[float] = mapped_column(Decimal(10,2), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus, name="status"), nullable=False)
    booked_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    cancelled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    event_id: Mapped[int] = mapped_column(ForeignKey(), nullable=True)
    attendee_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)
    