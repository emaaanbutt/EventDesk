from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimeStamp

if TYPE_CHECKING:
    from app.models.events import Event


class Category(Base, TimeStamp):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(255), unique=True, nullable=False)

    events: Mapped[list[Event]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
    )
   