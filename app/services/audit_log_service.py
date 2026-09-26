from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.role_policy import Action
from app.models.users import User
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit_logs import AuditLogFilters, AuditLogListResponse, AuditLogResponse
from app.services.authorization_service import authorize


async def get_audit_logs(
    actor: User, filters: AuditLogFilters, db: AsyncSession
) -> AuditLogListResponse:
    authorize(actor, Action.audit_logs_view)
    logs, total = await AuditLogRepository.list_logs(filters.page, filters.page_size, db)
    return AuditLogListResponse(
        items=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
    )


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
