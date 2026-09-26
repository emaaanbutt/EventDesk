from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit_logs import AuditLog


class AuditLogRepository:
    @staticmethod
    async def list_logs(
        page: int, page_size: int, db: AsyncSession
    ) -> tuple[list[AuditLog], int]:
        total = await db.scalar(select(func.count(AuditLog.id)))
        result = await db.execute(
            select(AuditLog)
            .options(selectinload(AuditLog.actor))
            .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    @staticmethod
    async def create(
        actor_user_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: UUID,
        details: dict[str, Any] | None,
        db: AsyncSession,
    ) -> AuditLog:
        log = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
        )
        db.add(log)
        await db.flush()
        return log
