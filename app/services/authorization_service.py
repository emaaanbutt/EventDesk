from __future__ import annotations

from uuid import UUID

from fastapi import HTTPException, status

from app.core.role_policy import Action, ROLE_PERMISSIONS
from app.models.enums import PermissionScope
from app.models.users import User


def authorize(actor: User, action: Action | str, owner_id: UUID | None = None) -> None:
    try:
        selected_action = Action(action)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action not permitted") from None

    role_permissions = ROLE_PERMISSIONS.get(actor.role)
    if role_permissions is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action not permitted")

    scope = role_permissions.get(selected_action)
    if scope in (PermissionScope.global_, PermissionScope.any):
        return

    if scope in (PermissionScope.self, PermissionScope.own, PermissionScope.own_event) and owner_id is not None and actor.id == owner_id:
        return

    # Missing permission, missing owner ID, wrong owner, or unknown scope: deny.
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action not permitted")
