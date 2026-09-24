from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.role_policy import Action
from app.core.security import hash_password, verify_password
from app.models.enums import Role
from app.models.users import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse, UserUpdate, validate_password_strength
from app.services.authorization_service import authorize


def _require_available(actor: User) -> None:
    if not actor.is_active or actor.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is unavailable")


async def _get_target(user_id: UUID, db: AsyncSession) -> User:
    user = await UserRepository.get_by_id(user_id, db)
    if user is None or user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def update_profile(actor: User, payload: UserUpdate, db: AsyncSession) -> UserResponse:
    _require_available(actor)
    authorize(actor, Action.profile_update, owner_id=actor.id)

    changes = payload.model_dump(exclude_unset=True)
    if not changes or any(value is None for value in changes.values()):
        raise HTTPException(status_code=422, detail="Provide a non-null name or email")
    if "name" in changes and not changes["name"].strip():
        raise HTTPException(status_code=422, detail="Name cannot be empty")

    if "email" in changes:
        existing = await UserRepository.get_by_email(changes["email"], db)
        if existing is not None and existing.id != actor.id:
            raise HTTPException(status_code=409, detail="Email already exists")

    try:
        user = await UserRepository.update_user(actor.id, payload, db)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists") from None

    await db.refresh(user)
    return UserResponse.model_validate(user)


async def change_password(
    actor: User, current_password: str, new_password: str, db: AsyncSession
) -> None:
    _require_available(actor)
    authorize(actor, Action.password_change, owner_id=actor.id)
    if not verify_password(current_password, actor.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    try:
        validate_password_strength(new_password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    if verify_password(new_password, actor.password_hash):
        raise HTTPException(status_code=409, detail="New password must differ from current password")

    await UserRepository.set_password_hash(actor, hash_password(new_password), db)
    await RefreshTokenRepository.revoke_all_for_user(actor.id, db)
    await db.commit()


async def list_users(actor: User, db: AsyncSession) -> list[UserResponse]:
    _require_available(actor)
    authorize(actor, Action.users_list)
    users = await UserRepository.get_all(db)
    return [UserResponse.model_validate(user) for user in users]


async def change_role(actor: User, user_id: UUID, new_role: Role, db: AsyncSession) -> UserResponse:
    """Change another user's role; admin only."""
    _require_available(actor)
    authorize(actor, Action.users_role_change)
    target = await _get_target(user_id, db)
    if target.id == actor.id:
        raise HTTPException(status_code=409, detail="You cannot change your own role")
    try:
        role = Role(new_role)
    except (ValueError, TypeError):
        raise HTTPException(status_code=422, detail="Invalid role") from None
    if target.role != role:
        await UserRepository.set_role(target, role, db)
        await RefreshTokenRepository.revoke_all_for_user(target.id, db)
        await db.commit()
        await db.refresh(target)
    return UserResponse.model_validate(target)


async def set_active(actor: User, user_id: UUID, is_active: bool, db: AsyncSession) -> UserResponse:
    """Activate/deactivate an account; admin only."""
    _require_available(actor)
    authorize(actor, Action.users_active_change)
    if not isinstance(is_active, bool):
        raise HTTPException(status_code=422, detail="is_active must be a boolean")
    target = await _get_target(user_id, db)
    if target.id == actor.id and not is_active:
        raise HTTPException(status_code=409, detail="You cannot deactivate your own account")
    if target.is_active != is_active:
        await UserRepository.set_active(target, is_active, db)
        if not is_active:
            await RefreshTokenRepository.revoke_all_for_user(target.id, db)
        await db.commit()
        await db.refresh(target)
    return UserResponse.model_validate(target)


async def soft_delete_user(actor: User, user_id: UUID, db: AsyncSession) -> None:
    """Mark another account deleted without removing its database row; admin only."""
    _require_available(actor)
    authorize(actor, Action.users_delete)
    target = await _get_target(user_id, db)
    if target.id == actor.id:
        raise HTTPException(status_code=409, detail="You cannot delete your own account")
    await UserRepository.soft_delete(target, datetime.now(timezone.utc), db)
    await RefreshTokenRepository.revoke_all_for_user(target.id, db)
    await db.commit()
