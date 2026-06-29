import pytest
import asyncio
from observability.event_bus import EventBus
from observability.events import ExecutionStarted
from transport.connection_manager import ConnectionManager
from transport.transport_adapter import TransportAdapter

class MockConnectionManager(ConnectionManager):
    def __init__(self):
        super().__init__()
        self.broadcasts = []
        
    async def broadcast(self, event_name, envelope):
        self.broadcasts.append((event_name, envelope))

@pytest.fixture
def event_bus():
    # Use a fresh instance for testing
    bus = EventBus()
    return bus

@pytest.fixture
def connection_manager():
    return MockConnectionManager()

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.anyio
async def test_transport_adapter_translates_event(event_bus, connection_manager):
    adapter = TransportAdapter(event_bus, connection_manager)
    
    event = ExecutionStarted(timestamp_ms=1000, execution_id="exec-1", correlation_id="exec-1")
    
    # Normally this uses asyncio.get_running_loop(), so we must be inside an async test
    event_bus.emit(event)
    
    # Yield to let the create_task run
    await asyncio.sleep(0.01)
    
    assert len(connection_manager.broadcasts) == 1
    event_name, envelope = connection_manager.broadcasts[0]
    
    assert event_name == "ExecutionStarted"
    assert envelope.type == "ExecutionStarted"
    assert envelope.executionId == "exec-1"
    assert envelope.payload["correlation_id"] == "exec-1"
