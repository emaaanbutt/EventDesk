from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PermissionScope, Role
from app.models.permissions import Permission
from app.models.role_permissions import RolePermission


class PermissionRepository:
    @staticmethod
    async def get_scope(role: Role, code: str, db: AsyncSession) -> PermissionScope | None:
        result = await db.execute(
            select(RolePermission.scope)
            .join(Permission, RolePermission.permission_id == Permission.id)
            .where(
                RolePermission.role == role,
                Permission.code == code,
                Permission.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()
