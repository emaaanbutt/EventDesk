from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.dependencies import CurrentUser, DbSession, get_db
from app.schemas.catalog import CatalogItemCreate, CategoryResponse
from app.services import catalog_service

router = APIRouter(prefix="/categories", tags=["categories"], dependencies=[Depends(get_db)])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(db: DbSession) -> list[CategoryResponse]:
    return await catalog_service.list_categories(db)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CatalogItemCreate,
    actor: CurrentUser,
    db: DbSession,
) -> CategoryResponse:
    return await catalog_service.create_category(actor, payload, db)
