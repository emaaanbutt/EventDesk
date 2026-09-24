from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import Role
from app.models.users import User
from app.schemas.user import UserUpdate


class UserRepository:
    @staticmethod
    async def get_by_email(email: str, db: AsyncSession) -> User | None:
        result = await db.execute(select(User).where(User.email == email.lower().strip()))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(user_id: UUID | str, db: AsyncSession) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        name: str, email: str, password_hash: str, role: Role, db: AsyncSession
    ) -> User:
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
        )
        db.add(user)
        await db.flush()
        return user

    @staticmethod
    async def update_user(user_id: UUID | str, payload: UserUpdate, db: AsyncSession) -> User | None:
        user = await UserRepository.get_by_id(user_id, db)
        if user is None:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.flush()
        return user

    @staticmethod
    async def get_all(db: AsyncSession) -> list[User]:
        result = await db.execute(
            select(User).where(User.deleted_at.is_(None)).order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def set_active(user: User, is_active: bool, db: AsyncSession) -> User:
        user.is_active = is_active
        await db.flush()
        return user

    @staticmethod
    async def set_role(user: User, role: Role, db: AsyncSession) -> User:
        user.role = role
        await db.flush()
        return user

    @staticmethod
    async def set_password_hash(user: User, password_hash: str, db: AsyncSession) -> None:
        user.password_hash = password_hash
        await db.flush()

    @staticmethod
    async def soft_delete(user: User, deleted_at: datetime, db: AsyncSession) -> None:
        user.deleted_at = deleted_at
        user.is_active = False
        await db.flush()
