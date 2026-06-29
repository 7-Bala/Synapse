"""Instrumentation layer for Orchestrator to emit EventBus events."""

from core.orchestrator_callbacks import OrchestratorCallbacks
from observability.event_bus import EventBus
from observability.events import (
    ExecutionCreated, ExecutionStarted, ExecutionCompleted,
    TickStarted, TickCompleted,
    AgentStarted, AgentCompleted, AgentFailed,
    BlackboardUpdated, BlackboardSnapshotCreated,
    ConsensusStarted, ConsensusCompleted,
    EvidenceAdded, EvidenceResolved
)

class EventBusInstrumentation(OrchestratorCallbacks):
    """Listens to Orchestrator callbacks and emits strongly-typed events to the EventBus."""

    def __init__(self):
        self.event_bus = EventBus.get_instance()

    def on_execution_created(self, execution_id: str) -> None:
        self.event_bus.emit(ExecutionCreated(correlation_id=execution_id))

    def on_execution_started(self, execution_id: str) -> None:
        self.event_bus.emit(ExecutionStarted(correlation_id=execution_id))

    def on_execution_completed(self, execution_id: str) -> None:
        self.event_bus.emit(ExecutionCompleted(correlation_id=execution_id))

    def on_evidence_added(self, execution_id: str, evidence_id: str) -> None:
        self.event_bus.emit(EvidenceAdded(correlation_id=execution_id, evidence_id=evidence_id))

    def on_evidence_resolved(self, execution_id: str, evidence_id: str) -> None:
        self.event_bus.emit(EvidenceResolved(correlation_id=execution_id, evidence_id=evidence_id))

    def on_tick_started(self, execution_id: str, tick_id: int) -> None:
        self.event_bus.emit(TickStarted(correlation_id=execution_id, tick_id=tick_id))

    def on_tick_completed(self, execution_id: str, tick_id: int) -> None:
        self.event_bus.emit(TickCompleted(correlation_id=execution_id, tick_id=tick_id))

    def on_agent_started(self, execution_id: str, agent_id: str, tick_id: int) -> None:
        self.event_bus.emit(AgentStarted(correlation_id=execution_id, agent_id=agent_id, tick_id=tick_id))

    def on_agent_completed(self, execution_id: str, agent_id: str, tick_id: int, latency_ms: int) -> None:
        self.event_bus.emit(AgentCompleted(correlation_id=execution_id, agent_id=agent_id, tick_id=tick_id, latency_ms=latency_ms))

    def on_agent_failed(self, execution_id: str, agent_id: str, tick_id: int, error: str) -> None:
        self.event_bus.emit(AgentFailed(correlation_id=execution_id, agent_id=agent_id, tick_id=tick_id, error=error))

    def on_blackboard_updated(self, execution_id: str, tick_id: int, agent_id: str) -> None:
        self.event_bus.emit(BlackboardUpdated(correlation_id=execution_id, tick_id=tick_id, agent_id=agent_id))

    def on_blackboard_snapshot_created(self, execution_id: str, tick_id: int) -> None:
        self.event_bus.emit(BlackboardSnapshotCreated(correlation_id=execution_id, tick_id=tick_id))

    def on_consensus_started(self, execution_id: str, tick_id: int) -> None:
        self.event_bus.emit(ConsensusStarted(correlation_id=execution_id, tick_id=tick_id))

    def on_consensus_completed(self, execution_id: str, tick_id: int, decision: str, confidence: float) -> None:
        self.event_bus.emit(ConsensusCompleted(correlation_id=execution_id, tick_id=tick_id, decision=decision, confidence=confidence))
