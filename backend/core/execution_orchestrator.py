"""ExecutionOrchestrator — the sole owner of execution lifecycle state.

This is the central runtime for Milestone 3. It:
  - Advances executions through: QUEUED → INITIALIZING → PLANNING → RUNNING
                                        → VALIDATING → COMPLETED / FAILED / CANCELLED
  - Dispatches each SpecialistAgent in order, emitting EventBus events at every step
  - Supports cooperative cancellation via asyncio.Event
  - Accumulates runtime metrics (tokens, cost, progress, agent counts) into
    the ExecutionRecord via the ExecutionStore
  - Is the ONLY component allowed to call store.update_execution_status()

No other code path may transition execution states directly.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional

from core.agents.base_agent import AgentPlan, AgentResult, ExecutionContext, SpecialistAgent
from core.agents.specialist_agents import default_agent_roster
from core.execution_store import get_execution_store
from observability.event_bus import EventBus
from observability.events import (
    AgentCompleted,
    AgentFailed,
    AgentStarted,
    ExecutionCompleted,
    ExecutionCreated,
    ExecutionFailed,
    ExecutionStarted,
    PlannerFinished,
    PlannerStarted,
    ValidationCompleted,
    ValidationStarted,
)
from schemas.execution import AgentNode, ExecutionState, TimelineEntry

logger = logging.getLogger(__name__)

# Progress weights assigned to each lifecycle phase (must sum to 1.0)
_PROGRESS_WEIGHTS: Dict[str, float] = {
    "INITIALIZING": 0.05,
    "PLANNING": 0.15,
    "RUNNING": 0.60,
    "VALIDATING": 0.15,
    "COMPLETING": 0.05,
}


class ExecutionOrchestrator:
    """Drives an execution through its full lifecycle.

    One instance is created per execution. It must NOT be reused.
    """

    def __init__(
        self,
        execution_id: str,
        agents: Optional[List[SpecialistAgent]] = None,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self._execution_id = execution_id
        self._agents = agents if agents is not None else default_agent_roster()
        self._bus = event_bus or EventBus.get_instance()
        self._store = get_execution_store()
        self._cancel_event: asyncio.Event = asyncio.Event()
        self._total_agents = len(self._agents)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def start_execution(self) -> None:
        """Entry point — drives the complete lifecycle from QUEUED to terminal state."""
        try:
            await self._run()
        except asyncio.CancelledError:
            self._transition(ExecutionState.CANCELLED)
            self._timeline("CANCELLED", "Execution cancelled by external request")
            raise
        except Exception as exc:  # noqa: BLE001
            logger.error("ExecutionOrchestrator: unhandled exception for %s: %s", self._execution_id, exc, exc_info=True)
            self._emit(ExecutionFailed(correlation_id=self._execution_id, error=str(exc)))
            self._transition(ExecutionState.FAILED)
            self._timeline("FAILED", f"Execution failed: {exc}")

    def request_cancel(self) -> None:
        """Requests cooperative cancellation. The orchestrator honours this at the next yield point."""
        logger.info("ExecutionOrchestrator: cancel requested for %s", self._execution_id)
        self._cancel_event.set()

    # ------------------------------------------------------------------
    # Lifecycle Implementation
    # ------------------------------------------------------------------

    async def _run(self) -> None:
        record = self._store.get_execution(self._execution_id)
        if record is None:
            raise RuntimeError(f"Execution {self._execution_id!r} not found in store")

        # ── Phase 1: INITIALIZING ────────────────────────────────────────
        self._transition(ExecutionState.INITIALIZING)
        self._emit(ExecutionCreated(correlation_id=self._execution_id))
        self._timeline("INITIALIZING", "Orchestrator initializing execution context")
        self._update_progress(0.02)
        await self._check_cancel()
        await asyncio.sleep(0.3)  # simulate setup latency

        # Build the immutable context for all agents
        context = ExecutionContext(
            execution_id=self._execution_id,
            user_prompt=record.userPrompt,
            execution_mode=record.executionMode,
        )

        # ── Phase 2: PLANNING ────────────────────────────────────────────
        self._transition(ExecutionState.PLANNING)
        self._emit(ExecutionStarted(correlation_id=self._execution_id))
        self._emit(PlannerStarted(correlation_id=self._execution_id, tick_id=1))
        self._timeline("PLANNING", "Orchestrator entering planning phase")
        self._update_progress(0.07)
        await self._check_cancel()
        await asyncio.sleep(0.2)

        # ── Phase 3: RUNNING — dispatch specialist agents ────────────────
        self._transition(ExecutionState.RUNNING)
        self._emit(PlannerFinished(correlation_id=self._execution_id, tick_id=1, plan="specialist_agents"))
        self._timeline("RUNNING", f"Dispatching {self._total_agents} specialist agents")

        completed_count = 0
        failed_count = 0

        # Progress allocated for RUNNING phase: 0.15 base + 0.60 for agents
        running_base = _PROGRESS_WEIGHTS["INITIALIZING"] + _PROGRESS_WEIGHTS["PLANNING"]

        for idx, agent in enumerate(self._agents):
            await self._check_cancel()

            # Skip the last agent (ValidationAgent is the second-to-last, ReporterAgent last)
            # Validation is its own phase; run PlannerAgent, ResearchAgent, ReasoningAgent here
            if idx == self._total_agents - 2:
                # Transition to VALIDATING before ValidationAgent
                break
            if idx == self._total_agents - 1:
                break

            agent_result = await self._run_agent(agent, context)
            if agent_result.success:
                completed_count += 1
            else:
                failed_count += 1

            # Update progress proportionally through the RUNNING window
            running_progress = running_base + _PROGRESS_WEIGHTS["RUNNING"] * (
                (idx + 1) / max(self._total_agents - 2, 1)
            )
            self._update_agent_metrics(completed_count, failed_count, running_progress)
            await asyncio.sleep(0)  # yield to event loop

        # ── Phase 4: VALIDATING ──────────────────────────────────────────
        await self._check_cancel()

        self._transition(ExecutionState.VALIDATING)
        self._emit(ValidationStarted(correlation_id=self._execution_id, validator_id="ValidationAgent"))
        self._timeline("VALIDATING", "Validation phase — running output quality checks")
        self._update_progress(running_base + _PROGRESS_WEIGHTS["RUNNING"] + 0.05)

        # Run ValidationAgent
        validation_agent = self._agents[-2]
        validation_result = await self._run_agent(validation_agent, context)
        if validation_result.success:
            completed_count += 1
        else:
            failed_count += 1

        self._emit(
            ValidationCompleted(
                correlation_id=self._execution_id,
                validator_id="ValidationAgent",
                status="PASSED" if validation_result.success else "FAILED",
                error=validation_result.error,
            )
        )

        await self._check_cancel()

        # Run ReporterAgent
        reporter_agent = self._agents[-1]
        reporter_result = await self._run_agent(reporter_agent, context)
        if reporter_result.success:
            completed_count += 1
        else:
            failed_count += 1

        # ── Phase 5: COMPLETING ──────────────────────────────────────────
        await self._check_cancel()
        self._update_progress(0.98)
        await asyncio.sleep(0.1)

        self._transition(ExecutionState.COMPLETED)
        self._emit(ExecutionCompleted(correlation_id=self._execution_id))
        self._timeline("COMPLETED", "All agents completed — execution finished successfully")
        self._update_agent_metrics(completed_count, failed_count, 1.0)

        logger.info(
            "ExecutionOrchestrator: %s completed — %d agents done, %d failed",
            self._execution_id,
            completed_count,
            failed_count,
        )

    # ------------------------------------------------------------------
    # Agent Dispatch
    # ------------------------------------------------------------------

    async def _run_agent(self, agent: SpecialistAgent, context: ExecutionContext) -> AgentResult:
        """Runs a single agent through plan → execute, emitting events."""
        agent_node_id = f"{self._execution_id}_{agent.name}"
        t0 = time.perf_counter()

        # Register agent node in DAG
        self._register_agent_node(agent_node_id, agent)
        self._emit(AgentStarted(correlation_id=self._execution_id, agent_id=agent.name, tick_id=1))
        self._timeline(f"{agent.name}.started", f"{agent.role} — beginning execution", agent=agent.name)

        record = self._store.get_execution(self._execution_id)
        if record:
            record.currentAgent = agent.name
            self._store.update_execution(record)

        try:
            plan: AgentPlan = await agent.plan(context)
            result: AgentResult = await agent.execute(plan, context)
        except Exception as exc:  # noqa: BLE001
            result = AgentResult(
                agent_name=agent.name,
                success=False,
                output="",
                error=str(exc),
                latency_ms=int((time.perf_counter() - t0) * 1000),
            )

        latency_ms = int((time.perf_counter() - t0) * 1000)

        if result.success:
            self._emit(
                AgentCompleted(
                    correlation_id=self._execution_id,
                    agent_id=agent.name,
                    tick_id=1,
                    latency_ms=latency_ms,
                    result_reference=result.output[:200] if result.output else None,
                )
            )
            self._timeline(
                f"{agent.name}.completed",
                f"{agent.role} — completed in {latency_ms}ms ({result.tokens_used} tokens)",
                agent=agent.name,
            )
            self._update_agent_node(agent_node_id, "COMPLETED", latency_ms, result)
        else:
            error_msg = result.error or "Unknown agent error"
            self._emit(
                AgentFailed(
                    correlation_id=self._execution_id,
                    agent_id=agent.name,
                    tick_id=1,
                    error=error_msg,
                )
            )
            self._timeline(
                f"{agent.name}.failed",
                f"{agent.role} — failed: {error_msg}",
                agent=agent.name,
            )
            self._update_agent_node(agent_node_id, "FAILED", latency_ms, result)

        # Accumulate metrics on execution record
        if record := self._store.get_execution(self._execution_id):
            record.totalTokens += result.tokens_used
            record.estimatedCost += (result.tokens_used / 1000) * 0.002
            self._store.update_execution(record)

        try:
            await agent.cleanup()
        except Exception:  # noqa: BLE001
            pass

        return result

    # ------------------------------------------------------------------
    # Store + Event helpers
    # ------------------------------------------------------------------

    def _transition(self, state: ExecutionState) -> None:
        """Transition the execution to a new state. ONLY this method may do so."""
        self._store.update_execution_status(self._execution_id, state)
        logger.debug("ExecutionOrchestrator: %s → %s", self._execution_id, state)

    def _emit(self, event) -> None:
        """Emit an event on the EventBus."""
        try:
            self._bus.emit(event)
        except Exception as exc:  # noqa: BLE001
            logger.warning("EventBus emit failed: %s", exc)

    def _timeline(self, event_name: str, detail: str = "", agent: Optional[str] = None) -> None:
        """Append a TimelineEntry to the immutable execution timeline."""
        entry = TimelineEntry(
            timestamp=time.time(),
            event=event_name,
            detail=detail,
            agent=agent,
        )
        self._store.append_timeline_entry(self._execution_id, entry)

    def _update_progress(self, progress: float) -> None:
        record = self._store.get_execution(self._execution_id)
        if record:
            record.progress = min(progress, 1.0)
            self._store.update_execution(record)

    def _update_agent_metrics(
        self, completed: int, failed: int, progress: float
    ) -> None:
        record = self._store.get_execution(self._execution_id)
        if record:
            record.completedAgentCount = completed
            record.failedAgentCount = failed
            record.activeAgentCount = max(0, self._total_agents - completed - failed)
            record.progress = min(progress, 1.0)
            self._store.update_execution(record)

    def _register_agent_node(self, node_id: str, agent: SpecialistAgent) -> None:
        nodes = self._store.get_agent_nodes(self._execution_id)
        parent_id = nodes[-1].id if nodes else None

        node = AgentNode(
            id=node_id,
            name=agent.name,
            role=agent.role,
            model=agent.model,
            status="RUNNING",
            parentId=parent_id,
        )
        self._store.add_agent_node(self._execution_id, node)

        if parent_id:
            parent = next((n for n in nodes if n.id == parent_id), None)
            if parent and node_id not in parent.childrenIds:
                parent.childrenIds.append(node_id)
                self._store.update_agent_node(self._execution_id, parent)

    def _update_agent_node(
        self, node_id: str, status: str, latency_ms: int, result: AgentResult
    ) -> None:
        nodes = self._store.get_agent_nodes(self._execution_id)
        node = next((n for n in nodes if n.id == node_id), None)
        if node:
            node.status = status
            node.latency = latency_ms
            node.tokenUsage = result.tokens_used
            node.confidence = result.confidence
            node.output = (result.output[:300] if result.output else result.error) or ""
            self._store.update_agent_node(self._execution_id, node)

    async def _check_cancel(self) -> None:
        """Raises asyncio.CancelledError if cancellation was requested."""
        if self._cancel_event.is_set():
            raise asyncio.CancelledError("Execution cancelled")
        # Yield to the event loop to allow other tasks to proceed
        await asyncio.sleep(0)


# ---------------------------------------------------------------------------
# Active orchestrator registry — used by the cancel API endpoint
# ---------------------------------------------------------------------------

_active_orchestrators: Dict[str, ExecutionOrchestrator] = {}


def register_orchestrator(execution_id: str, orchestrator: ExecutionOrchestrator) -> None:
    """Register an active orchestrator so it can be cancelled externally."""
    _active_orchestrators[execution_id] = orchestrator


def deregister_orchestrator(execution_id: str) -> None:
    """Remove a completed orchestrator from the registry."""
    _active_orchestrators.pop(execution_id, None)


def get_orchestrator(execution_id: str) -> Optional[ExecutionOrchestrator]:
    """Return the active orchestrator for the given execution, or None."""
    return _active_orchestrators.get(execution_id)
