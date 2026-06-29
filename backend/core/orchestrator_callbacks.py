"""Orchestrator lifecycle hooks to decouple business logic from observability."""

class OrchestratorCallbacks:
    """Base interface for observing orchestrator lifecycle events."""
    
    def on_execution_created(self, execution_id: str) -> None: pass
    def on_execution_started(self, execution_id: str) -> None: pass
    def on_execution_completed(self, execution_id: str) -> None: pass
    def on_evidence_added(self, execution_id: str, evidence_id: str) -> None: pass
    def on_evidence_resolved(self, execution_id: str, evidence_id: str) -> None: pass
    def on_tick_started(self, execution_id: str, tick_id: int) -> None: pass
    def on_tick_completed(self, execution_id: str, tick_id: int) -> None: pass
    def on_agent_started(self, execution_id: str, agent_id: str, tick_id: int) -> None: pass
    def on_agent_completed(self, execution_id: str, agent_id: str, tick_id: int, latency_ms: int) -> None: pass
    def on_agent_failed(self, execution_id: str, agent_id: str, tick_id: int, error: str) -> None: pass
    def on_blackboard_updated(self, execution_id: str, tick_id: int, agent_id: str) -> None: pass
    def on_blackboard_snapshot_created(self, execution_id: str, tick_id: int) -> None: pass
    def on_consensus_started(self, execution_id: str, tick_id: int) -> None: pass
    def on_consensus_completed(self, execution_id: str, tick_id: int, decision: str, confidence: float) -> None: pass
