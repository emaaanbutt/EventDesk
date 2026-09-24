from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tags import Tag


class TagRepository:
    @staticmethod
    async def get_by_name(name: str, db: AsyncSession) -> Tag | None:
        result = await db.execute(
            select(Tag).where(func.lower(Tag.name) == name, Tag.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_all(db: AsyncSession) -> list[Tag]:
        result = await db.execute(
            select(Tag)
            .where(Tag.deleted_at.is_(None))
            .order_by(Tag.name.asc(), Tag.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(name: str, db: AsyncSession) -> Tag:
        tag = Tag(name=name)
        db.add(tag)
        await db.flush()
        return tag
