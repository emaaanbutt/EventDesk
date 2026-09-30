from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import NotFoundError
from app.db.session import new_session
from app.schemas.notifications import NotificationResponse
from app.realtime.manager import manager

logger = logging.getLogger(__name__)


async def publish_event_availability(event_id: UUID) -> None:
    room = manager.find_event_room(event_id)
    if room is None:
        return
    async with room.lock:
        if not room.connections:
            return
        try:
            from app.services.event_service import get_event_availability

            async with new_session() as db:
                availability = await get_event_availability(event_id, db)
        except NotFoundError:
            await room.broadcast({"type": "event.unavailable", "data": {"event_id": str(event_id)}})
            return
        except (SQLAlchemyError, OSError):
            logger.exception("Could not load availability for event %s", event_id)
            return
        await room.broadcast(
            {"type": "event.availability", "data": availability.model_dump(mode="json")}
        )


async def publish_notification(notification: NotificationResponse, user_id: UUID) -> None:
    room = manager.find_user_room(user_id)
    if room is None:
        return
    async with room.lock:
        await room.broadcast(
            {"type": "notification.created", "data": notification.model_dump(mode="json")}
        )


async def publish_review_reply(event_id: UUID, review_id: UUID) -> None:
    room = manager.find_event_room(event_id)
    if room is None:
        return
    async with room.lock:
        await room.broadcast(
            {"type": "review.reply.created", "data": {"review_id": str(review_id)}}
        )
