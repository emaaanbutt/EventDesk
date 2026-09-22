from sqlalchemy import  DateTime, func, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base
from datetime import datetime

class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(VARCHAR, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(VARCHAR, nullable=False)   

    created_at: Mapped[datetime] = mapped_column(
                DateTime(timezone=True), server_default=func.now()
            )




    
    

   