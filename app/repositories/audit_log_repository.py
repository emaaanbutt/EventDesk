from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_logs import AuditLog


class AuditLogRepository:
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
