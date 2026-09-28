from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.users import User
from app.schemas.review_replies import ReviewReplyCreate, ReviewReplyResponse
from app.services import review_reply_service


router = APIRouter(prefix="/reviews/{review_id}/replies", tags=["review replies"])


@router.post("", response_model=ReviewReplyResponse, status_code=status.HTTP_201_CREATED)
async def reply_to_review(
    review_id: UUID,
    payload: ReviewReplyCreate,
    background_tasks: BackgroundTasks,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewReplyResponse:
    return await review_reply_service.reply_to_review(
        actor, review_id, payload, db, background_tasks
    )


@router.get("", response_model=list[ReviewReplyResponse])
async def list_review_replies(
    review_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[ReviewReplyResponse]:
    return await review_reply_service.list_review_replies(review_id, db)
