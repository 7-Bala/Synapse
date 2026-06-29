import pytest
import asyncio
from transport.connection_manager import ConnectionManager
from transport.transport_protocol import Connection
from transport.transport_events import EventEnvelope
import json

class MockConnection(Connection):
    def __init__(self, conn_id):
        self._conn_id = conn_id
        self.sent_payloads = []
        
    @property
    def connection_id(self) -> str:
        return self._conn_id
        
    async def send_payload(self, payload: str) -> None:
        self.sent_payloads.append(payload)

class FailingConnection(Connection):
    def __init__(self, conn_id):
        self._conn_id = conn_id
        
    @property
    def connection_id(self) -> str:
        return self._conn_id
        
    async def send_payload(self, payload: str) -> None:
        raise RuntimeError("Disconnected")

@pytest.fixture
def connection_manager():
    return ConnectionManager()

@pytest.fixture
def anyio_backend():
    return 'asyncio'

def test_register_and_unregister(connection_manager):
    conn = MockConnection("conn-1")
    connection_manager.register(conn)
    assert "conn-1" in connection_manager._connections
    
    connection_manager.unregister(conn)
    assert "conn-1" not in connection_manager._connections

@pytest.mark.anyio
async def test_broadcast(connection_manager):
    conn1 = MockConnection("conn-1")
    conn2 = MockConnection("conn-2")
    
    connection_manager.register(conn1)
    connection_manager.register(conn2)
    
    envelope = EventEnvelope(executionId="test", type="TestEvent", payload={})
    await connection_manager.broadcast("TestEvent", envelope)
    
    assert len(conn1.sent_payloads) == 1
    assert len(conn2.sent_payloads) == 1
    
    payload = json.loads(conn1.sent_payloads[0])
    assert payload["type"] == "TestEvent"

@pytest.mark.anyio
async def test_broadcast_handles_disconnects_gracefully(connection_manager):
    conn_fail = FailingConnection("conn-fail")
    conn_success = MockConnection("conn-ok")
    
    connection_manager.register(conn_fail)
    connection_manager.register(conn_success)
    
    envelope = EventEnvelope(executionId="test", type="TestEvent", payload={})
    
    # Should not raise exception
    await connection_manager.broadcast("TestEvent", envelope)
    
    assert len(conn_success.sent_payloads) == 1

@pytest.mark.anyio
async def test_duplicate_connection_handling(connection_manager):
    conn1 = MockConnection("conn-1")
    conn1_dup = MockConnection("conn-1")
    
    connection_manager.register(conn1)
    connection_manager.register(conn1_dup)
    
    # It overwrites
    assert len(connection_manager._connections) == 1
    assert connection_manager._connections["conn-1"] is conn1_dup
