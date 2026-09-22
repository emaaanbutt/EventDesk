from sqlalchemy import  DateTime, func, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base
from datetime import datetime
from typing import Any
from sqlalchemy.dialects.postgresql import JSONB


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_user_id: Mapped[int] = mapped_column(ForeignKey(), nullable=True)
    action: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    entity_type: Mapped[str] = mapped_column(VARCHAR, nullable=False)
    entity_id: Mapped[str] = mapped_column(nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(
                DateTime(timezone=True), server_default=func.now()
            )




    
    

   