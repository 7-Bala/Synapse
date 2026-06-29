"""Protocol-agnostic transport abstractions for the Synapse backend."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional


class Connection(ABC):
    """Abstract connection representing a connected client."""

    @property
    @abstractmethod
    def connection_id(self) -> str:
        """Unique identifier for the connection."""
        pass
        
    @abstractmethod
    async def send_payload(self, payload: str) -> None:
        """Send a string payload over the connection."""
        pass


class EventPublisher(ABC):
    """Abstract interface for publishing events to connected clients."""

    @abstractmethod
    async def publish(self, event_name: str, payload: Dict[str, Any]) -> None:
        """Publish an event to all interested clients."""
        pass


class CommandReceiver(ABC):
    """Abstract interface for receiving commands from clients."""

    @abstractmethod
    def register_command_handler(self, command_name: str, handler: Callable[..., Any]) -> None:
        """Register a handler for a specific command type."""
        pass


class TransportProtocol(EventPublisher, CommandReceiver, ABC):
    """Base protocol combining publishing and receiving capabilities."""

    @abstractmethod
    async def start(self) -> None:
        """Start the transport protocol."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the transport protocol."""
        pass
