from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.users import User
from app.schemas.notifications import NotificationFilters, NotificationListResponse
from app.services import notification_service


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/me", response_model=NotificationListResponse)
async def get_my_notifications(
    filters: Annotated[NotificationFilters, Query()],
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationListResponse:
    return await notification_service.get_my_notifications(actor, filters, db)
