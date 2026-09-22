from sqlalchemy import  DateTime, func, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base
from datetime import datetime


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token_hash: Mapped[str] = mapped_column(VARCHAR, unique=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
                DateTime(timezone=True), server_default=func.now()
            )

    expires_at: Mapped[datetime] = mapped_column(
                    DateTime(timezone=True), nullable=False
                )

    revoked_at: Mapped[datetime] = mapped_column(
                        DateTime(timezone=True), nullable=True
                    )

    user_id: Mapped[int] = mapped_column(ForeignKey(), nullable=False)
    
    

   