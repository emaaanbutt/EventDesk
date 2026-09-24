from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.categories import Category
from app.models.enums import EventStatus
from app.models.events import Event
from app.models.tags import Tag
from app.schemas.events import EventFilters


EVENT_FIELDS = {
    "title",
    "description",
    "venue",
    "starts_at",
    "ticket_price",
    "total_tickets",
    "category_id",
}


class EventRepository:
    @staticmethod
    async def get_by_id(event_id: UUID, db: AsyncSession) -> Event | None:
        result = await db.execute(
            select(Event)
            .options(selectinload(Event.category), selectinload(Event.tags))
            .where(Event.id == event_id, Event.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id_for_update(event_id: UUID, db: AsyncSession) -> Event | None:
        result = await db.execute(
            select(Event)
            .options(selectinload(Event.category), selectinload(Event.tags))
            .where(Event.id == event_id, Event.deleted_at.is_(None))
            .with_for_update()
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_event(
        values: dict[str, Any],
        organizer_id: UUID,
        status: EventStatus,
        tags: list[Tag],
        db: AsyncSession,
    ) -> Event:
        if not values.keys() <= EVENT_FIELDS:
            raise ValueError("Unknown event field")
        event = Event(**values, organizer_id=organizer_id, status=status, tags=tags)
        db.add(event)
        await db.flush()
        await db.refresh(event, attribute_names=["category", "tags", "created_at", "updated_at"])
        return event

    @staticmethod
    async def update_event(
        event: Event,
        changes: dict[str, Any],
        tags: list[Tag] | None,
        db: AsyncSession,
    ) -> Event:
        if not changes.keys() <= EVENT_FIELDS:
            raise ValueError("Unknown event field")
        for field, value in changes.items():
            setattr(event, field, value)
        if tags is not None:
            event.tags = tags
        await db.flush()
        await db.refresh(event, attribute_names=["category", "tags", "updated_at"])
        return event

    @staticmethod
    async def set_status(event: Event, status: EventStatus, db: AsyncSession) -> Event:
        event.status = status
        await db.flush()
        await db.refresh(event, attribute_names=["updated_at"])
        return event

    @staticmethod
    async def list_published(filters: EventFilters, db: AsyncSession) -> tuple[list[Event], int]:
        conditions = [Event.status == EventStatus.published, Event.deleted_at.is_(None)]
        if filters.search is not None:
            pattern = f"%{filters.search}%"
            conditions.append(
                or_(Event.title.ilike(pattern), Event.description.ilike(pattern), Event.venue.ilike(pattern))
            )
        if filters.category_id is not None:
            conditions.append(Event.category_id == filters.category_id)
        if filters.tag_id is not None:
            conditions.append(Event.tags.any(Tag.id == filters.tag_id))
        if filters.date_from is not None:
            conditions.append(Event.starts_at >= filters.date_from)
        if filters.date_to is not None:
            conditions.append(Event.starts_at <= filters.date_to)

        sort_columns = {
            "date_asc": Event.starts_at.asc(),
            "date_desc": Event.starts_at.desc(),
            "price_asc": Event.ticket_price.asc(),
            "price_desc": Event.ticket_price.desc(),
        }
        count_result = await db.execute(select(func.count(Event.id)).where(*conditions))
        total = count_result.scalar_one()
        result = await db.execute(
            select(Event)
            .options(selectinload(Event.category), selectinload(Event.tags))
            .where(*conditions)
            .order_by(sort_columns[filters.sort], Event.id.asc())
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
        return list(result.scalars().all()), total

    @staticmethod
    async def list_by_organizer(organizer_id: UUID, db: AsyncSession) -> list[Event]:
        result = await db.execute(
            select(Event)
            .options(selectinload(Event.category), selectinload(Event.tags))
            .where(Event.organizer_id == organizer_id, Event.deleted_at.is_(None))
            .order_by(Event.created_at.desc(), Event.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_tags_by_ids(tag_ids: list[UUID], db: AsyncSession) -> list[Tag]:
        if not tag_ids:
            return []
        result = await db.execute(
            select(Tag).where(Tag.id.in_(tag_ids), Tag.deleted_at.is_(None))
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_category_by_id(category_id: UUID, db: AsyncSession) -> Category | None:
        result = await db.execute(
            select(Category).where(Category.id == category_id, Category.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()
