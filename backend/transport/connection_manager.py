"""Protocol-agnostic connection manager."""

from typing import Dict, List, Optional
import logging
import asyncio

from .transport_protocol import Connection

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active abstract connections without knowing their protocol."""

    def __init__(self) -> None:
        self._connections: Dict[str, Connection] = {}

    def register(self, connection: Connection) -> None:
        """Register a new connection."""
        self._connections[connection.connection_id] = connection
        logger.info(f"Registered connection {connection.connection_id}. Total: {len(self._connections)}")

    def unregister(self, connection: Connection) -> None:
        """Unregister an existing connection."""
        if connection.connection_id in self._connections:
            del self._connections[connection.connection_id]
            logger.info(f"Unregistered connection {connection.connection_id}. Total: {len(self._connections)}")

    async def broadcast(self, event_name: str, payload: str) -> None:
        """Broadcast an event payload to all active connections."""
        if not self._connections:
            return
            
        tasks = [
            conn.send_payload(payload) 
            for conn in self._connections.values()
            if hasattr(conn, 'send_payload')
        ]
        
        if tasks:
            # Send concurrently, ignoring errors on disconnected sockets
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, Exception):
                    logger.debug(f"Broadcast error: {res}")

    async def send(self, connection_id: str, payload: str) -> None:
        """Send a payload to a specific connection."""
        if connection_id in self._connections:
            conn = self._connections[connection_id]
            if hasattr(conn, 'send_payload'):
                await conn.send_payload(payload)
