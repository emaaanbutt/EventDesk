from __future__ import annotations

import asyncio
from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class ConnectionRoom:
    def __init__(self) -> None:
        self.lock = asyncio.Lock()
        self.connections: set[WebSocket] = set()

    async def broadcast(self, message: dict) -> None:
        for socket in tuple(self.connections):
            try:
                await asyncio.wait_for(socket.send_json(message), timeout=2)
            except (WebSocketDisconnect, RuntimeError, OSError, TimeoutError):
                self.connections.discard(socket)


class ConnectionManager:
    def __init__(self) -> None:
        self._events: dict[UUID, ConnectionRoom] = defaultdict(ConnectionRoom)
        self._users: dict[UUID, ConnectionRoom] = defaultdict(ConnectionRoom)

    def event_room(self, event_id: UUID) -> ConnectionRoom:
        return self._events[event_id]

    def find_event_room(self, event_id: UUID) -> ConnectionRoom | None:
        return self._events.get(event_id)

    def user_room(self, user_id: UUID) -> ConnectionRoom:
        return self._users[user_id]

    def find_user_room(self, user_id: UUID) -> ConnectionRoom | None:
        return self._users.get(user_id)


manager = ConnectionManager()
