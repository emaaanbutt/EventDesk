from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, WebSocket
from starlette.websockets import WebSocketDisconnect

from app.db.session import AsyncSessionLocal
from app.realtime.auth import authenticate_notification_socket
from app.realtime.manager import manager
from app.services.event_service import get_event_availability


async def watch_event(socket: WebSocket, event_id: UUID) -> None:
    room = manager.event_room(event_id)
    try:
        async with room.lock:
            try:
                async with AsyncSessionLocal() as db:
                    availability = await get_event_availability(event_id, db)
            except HTTPException:
                await socket.close(code=1008)
                return
            await socket.accept()
            await socket.send_json(
                {"type": "event.availability", "data": availability.model_dump(mode="json")}
            )
            room.connections.add(socket)
        while True:
            await socket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        async with room.lock:
            room.connections.discard(socket)


async def watch_notifications(socket: WebSocket) -> None:
    identity = await authenticate_notification_socket(socket)
    if identity is None:
        return
    user_id, expires_at = identity
    room = manager.user_room(user_id)
    try:
        async with room.lock:
            await socket.send_json({"type": "connected"})
            room.connections.add(socket)
        while True:
            seconds_left = expires_at - datetime.now(timezone.utc).timestamp()
            if seconds_left <= 0:
                await socket.close(code=1008, reason="Access token expired")
                break
            try:
                await asyncio.wait_for(socket.receive_text(), timeout=seconds_left)
            except TimeoutError:
                await socket.close(code=1008, reason="Access token expired")
                break
    except WebSocketDisconnect:
        pass
    finally:
        async with room.lock:
            room.connections.discard(socket)
