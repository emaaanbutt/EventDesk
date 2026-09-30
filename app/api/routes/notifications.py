from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentUser, DbSession, get_current_user, get_db
from app.schemas.notifications import (
    NotificationFilters,
    NotificationListResponse,
    NotificationReadUpdate,
    NotificationResponse,
)
from app.services import notification_service

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    dependencies=[Depends(get_db), Depends(get_current_user)],
)


@router.get("/me", response_model=NotificationListResponse)
async def get_my_notifications(
    filters: Annotated[NotificationFilters, Query()],
    actor: CurrentUser,
    db: DbSession,
) -> NotificationListResponse:
    return await notification_service.get_my_notifications(actor, filters, db)


@router.patch("/{notification_id}/read-state", response_model=NotificationResponse)
async def update_read_state(
    notification_id: UUID,
    payload: NotificationReadUpdate,
    actor: CurrentUser,
    db: DbSession,
) -> NotificationResponse:
    return await notification_service.set_notification_read_state(
        actor, notification_id, payload, db
    )
