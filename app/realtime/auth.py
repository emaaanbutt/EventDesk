from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from json import JSONDecodeError
from uuid import UUID

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from app.core.security import decode_token
from app.db.session import AsyncSessionLocal
from app.repositories.user_repository import UserRepository


async def authenticate_notification_socket(socket: WebSocket) -> tuple[UUID, int] | None:
    await socket.accept()
    try:
        message = await asyncio.wait_for(socket.receive_json(), timeout=10)
    except WebSocketDisconnect:
        return None
    except (JSONDecodeError, TimeoutError):
        await socket.close(code=1008)
        return None

    if not isinstance(message, dict) or message.get("type") != "auth":
        await socket.close(code=1008)
        return None
    token = message.get("token")
    if not isinstance(token, str):
        await socket.close(code=1008)
        return None
    payload = decode_token(token, expected_type="access")
    if payload is None:
        await socket.close(code=1008)
        return None
    try:
        user_id = UUID(payload["sub"])
        expires_at = int(payload["exp"])
    except (ValueError, TypeError, KeyError):
        await socket.close(code=1008)
        return None
    if expires_at <= datetime.now(timezone.utc).timestamp():
        await socket.close(code=1008)
        return None

    async with AsyncSessionLocal() as db:
        user = await UserRepository.get_by_id(user_id, db)
    if user is None or user.deleted_at is not None or not user.is_active:
        await socket.close(code=1008)
        return None
    return user_id, expires_at
