from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from app.core.dependencies import get_db
from app.db.session import ping_database

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/db")
async def database_health() -> dict[str, str]:
    connected = await ping_database()
    return {"status": "connected" if connected else "disconnected"}
