import pytest
from fastapi.testclient import TestClient
from api.app import app
from core.execution_store import get_execution_store
from core.execution_listener import initialize_execution_listener
from schemas.execution import ExecutionRecord, ExecutionState, ExecutionMode, AgentNode
from observability.event_bus import EventBus
from observability.events import ExecutionCreated, ExecutionStarted, ExecutionCompleted, AgentStarted, AgentCompleted
import time

client = TestClient(app)

def test_store_operations():
    store = get_execution_store()
    exec_id = "test-exec-1"
    
    # Clean previous test executions if any
    record = store.get_execution(exec_id)
    if not record:
        record = ExecutionRecord(
            id=exec_id,
            status=ExecutionState.QUEUED,
            createdAt=time.time(),
            updatedAt=time.time(),
            userPrompt="Test Prompt",
            executionMode=ExecutionMode.SIMULATION
        )
        store.create_execution(record)
        
    retrieved = store.get_execution(exec_id)
    assert retrieved is not None
    assert retrieved.status == ExecutionState.QUEUED
    
    store.update_execution_status(exec_id, ExecutionState.RUNNING)
    assert store.get_execution(exec_id).status == ExecutionState.RUNNING
    
    # Add agent node
    node = AgentNode(
        id=f"{exec_id}_agent1",
        name="agent1",
        role="Test Role",
        model="test-model",
        status="IDLE"
    )
    store.add_agent_node(exec_id, node)
    nodes = store.get_agent_nodes(exec_id)
    assert len(nodes) == 1
    assert nodes[0].name == "agent1"

def test_listener_transitions():
    from testing.failure_injection import FailureInjector
    EventBus.clear()
    FailureInjector.clear()
    event_bus = EventBus.get_instance()
    # Initialize listener
    listener = initialize_execution_listener(event_bus)
    store = get_execution_store()
    
    exec_id = "listener-test-exec"
    
    # Emit events
    event_bus.emit(ExecutionCreated(correlation_id=exec_id))
    record = store.get_execution(exec_id)
    assert record is not None
    assert record.status == ExecutionState.QUEUED
    
    event_bus.emit(ExecutionStarted(correlation_id=exec_id))
    assert store.get_execution(exec_id).status == ExecutionState.RUNNING
    
    # Emit agent started
    event_bus.emit(AgentStarted(correlation_id=exec_id, agent_id="specialist-1", tick_id=1))
    nodes = store.get_agent_nodes(exec_id)
    assert len(nodes) == 1
    assert nodes[0].name == "specialist-1"
    assert nodes[0].status == "RUNNING"
    
    # Emit agent completed
    event_bus.emit(AgentCompleted(correlation_id=exec_id, agent_id="specialist-1", tick_id=1, latency_ms=100, result_reference="success"))
    nodes = store.get_agent_nodes(exec_id)
    assert nodes[0].status == "COMPLETED"
    assert nodes[0].latency == 100
    
    event_bus.emit(ExecutionCompleted(correlation_id=exec_id))
    assert store.get_execution(exec_id).status == ExecutionState.COMPLETED

def test_api_endpoints():
    # Test GET executions list
    response = client.get("/api/executions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Test POST trigger execution
    response = client.post("/api/executions", json={"prompt": "Run consensus test", "mode": "LIVE"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "QUEUED"
    assert data["userPrompt"] == "Run consensus test"
    exec_id = data["id"]
    
    # Test GET single execution
    response = client.get(f"/api/executions/{exec_id}")
    assert response.status_code == 200
    assert response.json()["id"] == exec_id
    
    # Test POST cancel
    response = client.post(f"/api/executions/{exec_id}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"
