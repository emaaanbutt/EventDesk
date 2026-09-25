from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.users import User
from app.schemas.notifications import (
    NotificationFilters,
    NotificationListResponse,
    NotificationReadUpdate,
    NotificationResponse,
)
from app.services import notification_service


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/me", response_model=NotificationListResponse)
async def get_my_notifications(
    filters: Annotated[NotificationFilters, Query()],
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationListResponse:
    return await notification_service.get_my_notifications(actor, filters, db)


@router.patch("/{notification_id}/read-state", response_model=NotificationResponse)
async def update_read_state(
    notification_id: UUID,
    payload: NotificationReadUpdate,
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationResponse:
    return await notification_service.set_notification_read_state(actor, notification_id, payload, db)
