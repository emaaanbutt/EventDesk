from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.categories import Category


class CategoryRepository:
    @staticmethod
    async def get_by_name(name: str, db: AsyncSession) -> Category | None:
        result = await db.execute(
            select(Category).where(func.lower(Category.name) == name, Category.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_all(db: AsyncSession) -> list[Category]:
        result = await db.execute(
            select(Category)
            .where(Category.deleted_at.is_(None))
            .order_by(Category.name.asc(), Category.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(name: str, db: AsyncSession) -> Category:
        category = Category(name=name)
        db.add(category)
        await db.flush()
        return category
