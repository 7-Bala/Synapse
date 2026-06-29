"""WebSocket protocol implementation for the transport layer."""

import asyncio
from typing import Any, Callable, Dict
import logging
from starlette.websockets import WebSocket, WebSocketState

from .transport_protocol import Connection, TransportProtocol
from .connection_manager import ConnectionManager

logger = logging.getLogger(__name__)

class WebSocketConnection(Connection):
    def __init__(self, websocket: WebSocket, connection_id: str):
        self.websocket = websocket
        self._connection_id = connection_id

    @property
    def connection_id(self) -> str:
        return self._connection_id

    async def send_payload(self, payload: str) -> None:
        if self.websocket.client_state == WebSocketState.CONNECTED:
            try:
                await self.websocket.send_text(payload)
            except Exception as e:
                logger.error(f"Failed to send payload to {self.connection_id}: {e}")


class WebSocketTransportProtocol(TransportProtocol):
    """Concrete transport protocol using WebSockets."""

    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.handlers: Dict[str, Callable[..., Any]] = {}

    async def start(self) -> None:
        logger.info("WebSocket transport protocol started.")

    async def stop(self) -> None:
        logger.info("WebSocket transport protocol stopped.")

    async def publish(self, event_name: str, payload: Dict[str, Any]) -> None:
        # Relies on the TransportAdapter -> ConnectionManager bridging,
        # but satisfies the EventPublisher interface.
        pass

    def register_command_handler(self, command_name: str, handler: Callable[..., Any]) -> None:
        self.handlers[command_name] = handler
