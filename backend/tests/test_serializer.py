import json
import pytest
from transport.transport_events import EventEnvelope
from transport.serializer import TransportSerializer

def test_serializer_produces_valid_json():
    envelope = EventEnvelope(executionId="exec-123", type="TestEvent", payload={"key": "value"})
    result = TransportSerializer.serialize_envelope(envelope)
    
    assert isinstance(result, str)
    
    parsed = json.loads(result)
    assert parsed["executionId"] == "exec-123"
    assert parsed["type"] == "TestEvent"
    assert parsed["payload"] == {"key": "value"}
