from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.dependencies import CurrentUser, DbSession, get_db
from app.schemas.catalog import CatalogItemCreate, TagResponse
from app.services import catalog_service

router = APIRouter(prefix="/tags", tags=["tags"], dependencies=[Depends(get_db)])


@router.get("", response_model=list[TagResponse])
async def list_tags(db: DbSession) -> list[TagResponse]:
    return await catalog_service.list_tags(db)


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    payload: CatalogItemCreate,
    actor: CurrentUser,
    db: DbSession,
) -> TagResponse:
    return await catalog_service.create_tag(actor, payload, db)
