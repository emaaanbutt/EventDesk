from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, WebSocket

from app.realtime import connections

router = APIRouter(prefix="/ws", tags=["realtime"])


@router.websocket("/events/{event_id}")
async def event_availability_socket(socket: WebSocket, event_id: UUID) -> None:
    await connections.watch_event(socket, event_id)


@router.websocket("/notifications")
async def notification_socket(socket: WebSocket) -> None:
    await connections.watch_notifications(socket)
