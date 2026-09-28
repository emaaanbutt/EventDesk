from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.users import User
from app.schemas.reviews import ReviewCreate, ReviewListResponse, ReviewResponse, ReviewUpdate
from app.services import review_service


router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    payload: ReviewCreate,
    background_tasks: BackgroundTasks,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    return await review_service.create_review(actor, payload, db, background_tasks)


@router.get("", response_model=ReviewListResponse)
async def list_event_reviews(
    event_id: UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> ReviewListResponse:
    return await review_service.list_event_reviews(event_id, page, page_size, db)


@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: UUID,
    payload: ReviewUpdate,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    return await review_service.update_review(actor, review_id, payload, db)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: UUID,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await review_service.delete_review(actor, review_id, db)
