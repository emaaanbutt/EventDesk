from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentUser, DbSession, get_current_user, get_db
from app.schemas.audit_logs import AuditLogFilters, AuditLogListResponse
from app.services import audit_log_service

router = APIRouter(
    prefix="/audit-logs",
    tags=["audit logs"],
    dependencies=[Depends(get_db), Depends(get_current_user)],
)


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    filters: Annotated[AuditLogFilters, Query()],
    actor: CurrentUser,
    db: DbSession,
) -> AuditLogListResponse:
    return await audit_log_service.get_audit_logs(actor, filters, db)
