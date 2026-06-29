"""Protocol-agnostic connection manager."""

from typing import Dict, List, Optional
import logging

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
        """Broadcast an event payload to all active connections.
        
        The actual sending logic must be implemented by the specific protocol
        by subclassing Connection and handling the network IO. This manager
        only acts as the registry.
        """
        # In a real implementation, this would iterate over self._connections
        # and invoke a protocol-specific send method on each Connection object.
        pass

    async def send(self, connection_id: str, payload: str) -> None:
        """Send a payload to a specific connection."""
        if connection_id in self._connections:
            pass
