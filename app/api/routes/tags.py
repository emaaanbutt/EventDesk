from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.users import User
from app.schemas.catalog import CatalogItemCreate, TagResponse
from app.services import catalog_service

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagResponse])
async def list_tags(db: AsyncSession = Depends(get_db)) -> list[TagResponse]:
    return await catalog_service.list_tags(db)


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    payload: CatalogItemCreate,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TagResponse:
    return await catalog_service.create_tag(actor, payload, db)
