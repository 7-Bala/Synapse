"""Transport adapter bridging the backend EventBus to canonical transport events."""

import logging
from typing import Any, Callable, Dict, Optional

from observability.event_bus import EventBus
from observability.events import BaseEvent

from .connection_manager import ConnectionManager
from .transport_events import EventEnvelope

logger = logging.getLogger(__name__)


class TransportAdapter:
    """Translates backend events into standard transport events without mutating state."""

    def __init__(self, event_bus: EventBus, connection_manager: ConnectionManager):
        self.event_bus = event_bus
        self.connection_manager = connection_manager
        self.execution_id = "unknown"  # Extracted from context/events

        # Subscribe to all EventBus telemetry
        self.event_bus.subscribe(self._handle_backend_event)

    def _handle_backend_event(self, event: BaseEvent) -> None:
        """Observe backend EventBus, transform, and push to connection manager."""
        import asyncio
        event_type = type(event).__name__
        
        envelope = EventEnvelope(
            executionId=getattr(event, "correlation_id", self.execution_id),
            type=event_type,
            payload=event.model_dump()
        )
        
        # Fire and forget into the current async event loop
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.connection_manager.broadcast(event_type, envelope))
        except RuntimeError:
            # If no running loop, we can't broadcast (e.g. some synchronous tests)
            pass
