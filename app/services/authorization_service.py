from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.role_policy import Action
from app.models.enums import PermissionScope
from app.models.users import User
from app.repositories.permission_repository import PermissionRepository


def _require_scope(actor: User, scope: PermissionScope | None, owner_id: UUID | None) -> None:
    if scope in (PermissionScope.global_, PermissionScope.any):
        return
    if (
        scope in (PermissionScope.self, PermissionScope.own, PermissionScope.own_event)
        and owner_id is not None
        and actor.id == owner_id
    ):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action not permitted")


async def authorize_db(
    actor: User, action: Action | str, db: AsyncSession, owner_id: UUID | None = None
) -> None:
    try:
        selected_action = Action(action)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action not permitted") from None

    scope = await PermissionRepository.get_scope(actor.role, selected_action.value, db)
    _require_scope(actor, scope, owner_id)
