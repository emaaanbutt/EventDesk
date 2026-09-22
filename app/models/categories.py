from sqlalchemy import  DateTime, func, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base
from datetime import datetime


class RecurrenceRule(Base):
    __tablename__ = "recurrence_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR, unique=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
                DateTime(timezone=True), nullable=False, server_default=func.now()
            )
    

   