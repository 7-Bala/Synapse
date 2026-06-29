import json
from .transport_events import EventEnvelope


class TransportSerializer:
    """Serializes EventEnvelope domain objects into transport payloads."""

    @staticmethod
    def serialize_envelope(envelope: EventEnvelope) -> str:
        """Serializes an EventEnvelope into a JSON string for transport.
        
        Args:
            envelope: The domain event envelope.
            
        Returns:
            str: The JSON serialized string.
        """
        return envelope.model_dump_json()
