from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, UniqueConstraint, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import PermissionScope, Role

if TYPE_CHECKING:
    from app.models.permissions import Permission


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role: Mapped[Role] = mapped_column(Enum(Role, name="role"), nullable=False)
    permission_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"), nullable=True
    )
    scope: Mapped[PermissionScope] = mapped_column(Enum(PermissionScope, name="permission_scope"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("role", "permission_id", "scope", name="uq_role_permission_scope"),
    )

    permission: Mapped[Permission | None] = relationship(back_populates="role_permissions")
   