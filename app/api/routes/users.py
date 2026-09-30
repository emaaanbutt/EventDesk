from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.dependencies import CurrentUser, DbSession, get_current_user, get_db
from app.schemas.user import ActiveChange, PasswordChange, RoleChange, UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(
    prefix="/users", tags=["users"], dependencies=[Depends(get_db), Depends(get_current_user)]
)


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    payload: UserUpdate,
    actor: CurrentUser,
    db: DbSession,
) -> UserResponse:
    return await user_service.update_profile(actor, payload, db)


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_my_password(
    payload: PasswordChange,
    actor: CurrentUser,
    db: DbSession,
) -> None:
    await user_service.change_password(actor, payload.current_password, payload.new_password, db)


@router.get("/", response_model=list[UserResponse])
async def get_users(
    actor: CurrentUser,
    db: DbSession,
) -> list[UserResponse]:
    return await user_service.list_users(actor, db)


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: UUID,
    payload: RoleChange,
    actor: CurrentUser,
    db: DbSession,
) -> UserResponse:
    return await user_service.change_role(actor, user_id, payload.new_role, db)


@router.patch("/{user_id}/active", response_model=UserResponse)
async def update_user_active_status(
    user_id: UUID,
    payload: ActiveChange,
    actor: CurrentUser,
    db: DbSession,
) -> UserResponse:
    return await user_service.set_active(actor, user_id, payload.is_active, db)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    actor: CurrentUser,
    db: DbSession,
) -> None:
    await user_service.soft_delete_user(actor, user_id, db)
