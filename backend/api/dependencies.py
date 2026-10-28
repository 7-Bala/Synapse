"""Shared dependencies for the FastAPI application."""

from observability.event_bus import EventBus
from transport.connection_manager import ConnectionManager
from transport.transport_adapter import TransportAdapter
from transport.websocket_protocol import WebSocketTransportProtocol

from core.execution_listener import initialize_execution_listener

# Global instances
event_bus = EventBus.get_instance()
connection_manager = ConnectionManager()
transport_adapter = TransportAdapter(event_bus, connection_manager)
transport_protocol = WebSocketTransportProtocol(connection_manager)

# Initialize execution listener to capture all events
initialize_execution_listener(event_bus)

def get_connection_manager() -> ConnectionManager:
    """Dependency provider for ConnectionManager."""
    return connection_manager

def get_transport_protocol() -> WebSocketTransportProtocol:
    """Dependency provider for WebSocketTransportProtocol."""
    return transport_protocol
