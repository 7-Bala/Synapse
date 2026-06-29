"""EventBus infrastructure for telemetry and observability."""

from typing import Callable, List, TypeVar
from .events import BaseEvent

TEvent = TypeVar("TEvent", bound=BaseEvent)


class EventBus:
    """A lightweight, synchronous event bus for observability telemetry.

    If disabled, degrades into a transparent no-op.
    """

    _instance = None

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._subscribers: List[Callable[[BaseEvent], None]] = []

    @classmethod
    def get_instance(cls, enabled: bool = True) -> "EventBus":
        """Singleton pattern for global event bus if needed."""
        if cls._instance is None:
            cls._instance = EventBus(enabled=enabled)
        return cls._instance

    @classmethod
    def clear(cls) -> None:
        """Reset the singleton (useful for testing)."""
        cls._instance = None

    def subscribe(self, callback: Callable[[BaseEvent], None]) -> None:
        """Register a listener callback."""
        self._subscribers.append(callback)

    def emit(self, event: BaseEvent) -> None:
        """Publish an event to all subscribers."""
        if not self.enabled:
            return

        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                # Observability must never crash or delay execution
                pass
