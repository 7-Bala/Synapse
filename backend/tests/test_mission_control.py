"""Unit tests for Milestone 4 — RuntimeSnapshotService and Mission Control API."""

import pytest
import uuid
import time
from core.execution_store import get_execution_store
from core.scheduler import get_scheduler
from core.runtime_snapshot import RuntimeSnapshotService
from schemas.execution import ExecutionRecord, ExecutionState, ExecutionMode

def make_test_record(status: ExecutionState, prompt: str = "Test prompt") -> ExecutionRecord:
    now = time.time()
    return ExecutionRecord(
        id=str(uuid.uuid4()),
        status=status,
        createdAt=now,
        updatedAt=now,
        userPrompt=prompt,
        executionMode=ExecutionMode.LIVE,
        metadata={},
    )

def test_snapshot_service_overview_metrics():
    store = get_execution_store()
    
    # Empty out previous executions for deterministic test checking
    store._executions.clear()
    
    # Create test executions
    r1 = make_test_record(ExecutionState.RUNNING)
    r1.totalTokens = 1500
    r1.estimatedCost = 0.003
    r1.currentAgent = "ReasoningAgent"
    store.create_execution(r1)
    
    r2 = make_test_record(ExecutionState.QUEUED)
    store.create_execution(r2)
    
    r3 = make_test_record(ExecutionState.COMPLETED)
    r3.totalTokens = 800
    r3.estimatedCost = 0.0016
    r3.startedAt = time.time() - 10
    r3.completedAt = time.time()
    r3.totalLatency = 10000 # 10s
    store.create_execution(r3)

    r4 = make_test_record(ExecutionState.FAILED)
    store.create_execution(r4)
    
    snapshot = RuntimeSnapshotService.get_snapshot()
    
    assert snapshot["activeExecutions"] == 1
    assert snapshot["queuedExecutions"] == 1
    assert snapshot["completedExecutions"] == 1
    assert snapshot["failedExecutions"] == 1
    assert snapshot["totalTokens"] == 2300
    assert snapshot["estimatedCost"] == pytest.approx(0.0046)
    assert snapshot["averageLatency"] == pytest.approx(10.0)

def test_snapshot_service_active_and_queued_lists():
    store = get_execution_store()
    store._executions.clear()
    
    r1 = make_test_record(ExecutionState.RUNNING)
    r1.currentAgent = "ResearchAgent"
    r1.startedAt = time.time() - 5.0
    store.create_execution(r1)
    
    r2 = make_test_record(ExecutionState.QUEUED)
    store.create_execution(r2)
    
    active = RuntimeSnapshotService.get_active_executions()
    queued = RuntimeSnapshotService.get_queued_executions()
    
    assert len(active) == 1
    assert active[0]["id"] == r1.id
    assert active[0]["currentAgent"] == "ResearchAgent"
    assert active[0]["elapsed"] >= 4.9
    
    assert len(queued) == 1
    assert queued[0]["id"] == r2.id
    assert queued[0]["position"] == 1

def test_snapshot_service_health():
    health = RuntimeSnapshotService.get_health()
    assert "overall" in health
    assert "scheduler" in health
    assert "eventBus" in health
    assert "store" in health
    assert "queueDepth" in health
    assert "workerCount" in health
    assert "activeExecutionCount" in health
