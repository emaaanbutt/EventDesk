from sqlalchemy import Integer, String, VARCHAR, Enum, Boolean, Text, DateTime, Decimal, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base, TimeStamp



class BookingSeat(Base):
    __tablename__ = "booking_seats"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey(), nullable=True)
    seat_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)

    __table_args__ = (
        UniqueConstraint("booking_id", "seat_id", name="uq_booking_seat")
    )
    