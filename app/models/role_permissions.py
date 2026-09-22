from sqlalchemy import  DateTime, func, VARCHAR, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, ForeignKey
from app.db.base import Base
from datetime import datetime
from enums import Role, PermissionScope


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[Role] = mapped_column(Enum(Role, name="role"), nullable=False)
    permission_id: Mapped[int] = mapped_column(ForeignKey(), nullable=True)
    scope: Mapped[PermissionScope] = mapped_column(Enum(PermissionScope, name="role"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
                DateTime(timezone=True), server_default=func.now()
            )

    ___table_args__ = (UniqueConstraint("role", "permission_id", name="uq_role_permission"))
    




    
    

   