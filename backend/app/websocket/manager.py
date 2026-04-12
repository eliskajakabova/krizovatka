import asyncio
import json
import threading
from collections import defaultdict
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)
        self._lock = threading.Lock()
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def connect(self, simulation_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        with self._lock:
            self.active_connections[simulation_id].append(websocket)

    def disconnect(self, simulation_id: str, websocket: WebSocket) -> None:
        with self._lock:
            if (
                simulation_id in self.active_connections
                and websocket in self.active_connections[simulation_id]
            ):
                self.active_connections[simulation_id].remove(websocket)
                if not self.active_connections[simulation_id]:
                    del self.active_connections[simulation_id]

    async def send_personal_message(
            self, websocket: WebSocket, message: dict) -> None:
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, simulation_id: str, message: dict) -> None:
        payload = json.dumps(message)
        dead_connections: list[WebSocket] = []

        with self._lock:
            connections = list(self.active_connections.get(simulation_id, []))

        for connection in connections:
            try:
                await connection.send_text(payload)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(simulation_id, connection)

    def broadcast_from_thread(self, simulation_id: str, message: dict) -> None:
        if self._loop is None:
            return

        asyncio.run_coroutine_threadsafe(
            self.broadcast(simulation_id, message),
            self._loop,
        )
