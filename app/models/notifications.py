from sqlalchemy import VARCHAR, Enum, Boolean, Text, DateTime,func
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base, TimeStamp
from enums import BookingType
from datetime import datetime

class Notification(Base, TimeStamp):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey(), nullable=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey(), nullable=True)
    status: Mapped[BookingType] = mapped_column(Enum(BookingType, name="status"), nullable=False)
    title: Mapped[str] = mapped_column(VARCHAR(255))
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        )
    read_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), nullable=True
        )
    
    user_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)
    review_id: Mapped[int] = mapped_column(ForeignKey(), nullable=True)
    