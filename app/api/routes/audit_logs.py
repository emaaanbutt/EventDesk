from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.users import User
from app.schemas.audit_logs import AuditLogFilters, AuditLogListResponse
from app.services import audit_log_service


router = APIRouter(prefix="/audit-logs", tags=["audit logs"])


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    filters: Annotated[AuditLogFilters, Query()],
    actor: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AuditLogListResponse:
    return await audit_log_service.get_audit_logs(actor, filters, db)
