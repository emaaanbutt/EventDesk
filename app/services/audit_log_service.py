from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.role_policy import Action
from app.repositories.audit_log_repository import AuditLogRepository


async def record_audit_log(
    actor_user_id: UUID | None,
    action: Action,
    entity_type: str,
    entity_id: UUID,
    details: dict[str, Any] | None,
    db: AsyncSession,
) -> None:
    await AuditLogRepository.create(
        actor_user_id=actor_user_id,
        action=action.value,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        db=db,
    )
