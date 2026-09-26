"""Rules for the category and tag choices used by events."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.role_policy import Action
from app.models.users import User
from app.repositories.category_repository import CategoryRepository
from app.repositories.tag_repository import TagRepository
from app.schemas.catalog import CatalogItemCreate, CategoryResponse, TagResponse
from app.services.authorization_service import authorize_db


async def list_categories(db: AsyncSession) -> list[CategoryResponse]:
    categories = await CategoryRepository.list_all(db)
    return [CategoryResponse.model_validate(category) for category in categories]


async def list_tags(db: AsyncSession) -> list[TagResponse]:
    tags = await TagRepository.list_all(db)
    return [TagResponse.model_validate(tag) for tag in tags]


async def create_category(
    actor: User, payload: CatalogItemCreate, db: AsyncSession
) -> CategoryResponse:
    if not actor.is_active or actor.deleted_at is not None:
        raise HTTPException(status_code=403, detail="User account is unavailable")
    await authorize_db(actor, Action.categories_create, db)
    if await CategoryRepository.get_by_name(payload.name, db) is not None:
        raise HTTPException(status_code=409, detail="Category already exists")

    try:
        category = await CategoryRepository.create(payload.name, db)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Category already exists") from None
    return CategoryResponse.model_validate(category)


async def create_tag(actor: User, payload: CatalogItemCreate, db: AsyncSession) -> TagResponse:
    if not actor.is_active or actor.deleted_at is not None:
        raise HTTPException(status_code=403, detail="User account is unavailable")
    await authorize_db(actor, Action.tags_create, db)
    if await TagRepository.get_by_name(payload.name, db) is not None:
        raise HTTPException(status_code=409, detail="Tag already exists")

    try:
        tag = await TagRepository.create(payload.name, db)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Tag already exists") from None
    return TagResponse.model_validate(tag)
