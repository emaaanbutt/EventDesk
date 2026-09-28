from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.role_policy import Action
from app.models.users import User
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.audit_logs import AuditLogFilters, AuditLogListResponse, AuditLogResponse
from app.services.authorization_service import authorize_db


async def get_audit_logs(
    actor: User, filters: AuditLogFilters, db: AsyncSession
) -> AuditLogListResponse:
    await authorize_db(actor, Action.audit_logs_view, db)
    logs, total = await AuditLogRepository.list_logs(filters.page, filters.page_size, db)
    names = await AuditLogRepository.entity_names(logs, db)
    items = []
    for log in logs:
        entity_id = log.entity_id
        if log.entity_type == "booking" and log.details:
            entity_id = UUID(log.details["event_id"]) if log.details.get("event_id") else None
        items.append(
            AuditLogResponse.model_validate(log).model_copy(
                update={"entity_name": names.get(entity_id)}
            )
        )
    return AuditLogListResponse(
        items=items,
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
