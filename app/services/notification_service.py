from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.role_policy import Action
from app.models.users import User
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notifications import NotificationResponse
from app.services.authorization_service import authorize


async def get_my_notifications(actor: User, db: AsyncSession) -> list[NotificationResponse]:
    if not actor.is_active or actor.deleted_at is not None:
        raise HTTPException(status_code=403, detail="User account is unavailable")
    authorize(actor, Action.notifications_view, owner_id=actor.id)
    notifications = await NotificationRepository.list_for_user(actor.id, db)
    return [NotificationResponse.model_validate(item) for item in notifications]
