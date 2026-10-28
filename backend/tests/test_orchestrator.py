"""Unit tests for Milestone 3 — ExecutionOrchestrator and ExecutionScheduler.

All async tests run under asyncio (enforced by conftest.py anyio_backend fixture).
The production runtime uses native asyncio primitives exclusively.
"""

import asyncio
import time
import uuid
import pytest

from core.agents.base_agent import (
    AgentPlan,
    AgentResult,
    ExecutionContext,
    SpecialistAgent,
)
from core.agents.specialist_agents import (
    PlannerAgent,
    default_agent_roster,
)
from core.execution_orchestrator import ExecutionOrchestrator
from core.execution_store import InMemoryExecutionStore
from core.scheduler import ExecutionScheduler
from observability.event_bus import EventBus
from schemas.execution import ExecutionRecord, ExecutionState, ExecutionMode


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_record(execution_id: str, prompt: str = "Test prompt") -> ExecutionRecord:
    now = time.time()
    return ExecutionRecord(
        id=execution_id,
        status=ExecutionState.QUEUED,
        createdAt=now,
        updatedAt=now,
        userPrompt=prompt,
        executionMode=ExecutionMode.LIVE,
        metadata={},
    )


class IsolatedOrchestrator(ExecutionOrchestrator):
    """ExecutionOrchestrator with injected store and bus for test isolation."""

    def __init__(self, execution_id: str, agents=None, store=None, event_bus=None):
        super().__init__(execution_id=execution_id, agents=agents, event_bus=event_bus)
        if store is not None:
            self._store = store


def make_5_agents(names=None):
    default_names = ["PlannerAgent", "ResearchAgent", "ReasoningAgent", "ValidationAgent", "ReporterAgent"]
    return [FastSuccessAgent(n) for n in (names or default_names)]


# ---------------------------------------------------------------------------
# Deterministic test agents (no random failures, zero latency)
# ---------------------------------------------------------------------------


class FastSuccessAgent(SpecialistAgent):
    """Always succeeds instantly."""

    def __init__(self, name: str = "FastAgent"):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def role(self) -> str:
        return "Test Agent"

    @property
    def model(self) -> str:
        return "test-model"

    async def plan(self, context: ExecutionContext) -> AgentPlan:
        return AgentPlan(agent_name=self.name, steps=["step1"], estimated_tokens=100)

    async def execute(self, plan: AgentPlan, context: ExecutionContext) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            success=True,
            output=f"{self.name} completed",
            tokens_used=100,
            latency_ms=1,
            confidence=1.0,
        )

    async def validate(self, result: AgentResult, context: ExecutionContext) -> bool:
        return True

    async def cleanup(self) -> None:
        pass


class FastFailingAgent(SpecialistAgent):
    """Always fails instantly."""

    def __init__(self, name: str = "FailingAgent"):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def role(self) -> str:
        return "Failing Test Agent"

    @property
    def model(self) -> str:
        return "test-model"

    async def plan(self, context: ExecutionContext) -> AgentPlan:
        return AgentPlan(agent_name=self.name, steps=["fail"], estimated_tokens=0)

    async def execute(self, plan: AgentPlan, context: ExecutionContext) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            success=False,
            output="",
            error="Intentional test failure",
            tokens_used=0,
            latency_ms=1,
            confidence=0.0,
        )

    async def validate(self, result: AgentResult, context: ExecutionContext) -> bool:
        return False

    async def cleanup(self) -> None:
        pass


# ---------------------------------------------------------------------------
# SpecialistAgent interface tests (synchronous — use asyncio.run)
# ---------------------------------------------------------------------------


class TestSpecialistAgentInterface:
    def test_fast_success_agent_name(self):
        assert FastSuccessAgent("TestAgent").name == "TestAgent"

    def test_fast_success_agent_properties(self):
        agent = FastSuccessAgent()
        assert agent.role == "Test Agent"
        assert agent.model == "test-model"

    def test_fast_agent_plan(self):
        agent = FastSuccessAgent("A")
        context = ExecutionContext(execution_id="x", user_prompt="p", execution_mode="LIVE")
        plan = asyncio.run(agent.plan(context))
        assert plan.agent_name == "A"
        assert len(plan.steps) > 0

    def test_fast_agent_execute_success(self):
        agent = FastSuccessAgent("A")
        context = ExecutionContext(execution_id="x", user_prompt="p", execution_mode="LIVE")

        async def _run():
            plan = await agent.plan(context)
            return await agent.execute(plan, context)

        result = asyncio.run(_run())
        assert result.success is True
        assert result.tokens_used == 100

    def test_failing_agent_execute_failure(self):
        agent = FastFailingAgent()
        context = ExecutionContext(execution_id="x", user_prompt="p", execution_mode="LIVE")

        async def _run():
            plan = await agent.plan(context)
            return await agent.execute(plan, context)

        result = asyncio.run(_run())
        assert result.success is False
        assert result.error == "Intentional test failure"


# ---------------------------------------------------------------------------
# Mock specialist agents
# ---------------------------------------------------------------------------


class TestMockSpecialistAgents:
    def test_default_roster_has_five_agents(self):
        agents = default_agent_roster()
        assert len(agents) == 5
        names = [a.name for a in agents]
        assert "PlannerAgent" in names
        assert "ResearchAgent" in names
        assert "ReasoningAgent" in names
        assert "ValidationAgent" in names
        assert "ReporterAgent" in names

    def test_planner_agent_properties(self):
        agent = PlannerAgent()
        assert agent.name == "PlannerAgent"
        assert agent.model is not None

    def test_planner_agent_plan_returns_steps(self):
        agent = PlannerAgent()
        context = ExecutionContext(execution_id="x", user_prompt="Test", execution_mode="LIVE")
        plan = asyncio.run(agent.plan(context))
        assert len(plan.steps) > 0
        assert plan.agent_name == "PlannerAgent"


# ---------------------------------------------------------------------------
# ExecutionOrchestrator lifecycle tests (async — asyncio backend via conftest)
# ---------------------------------------------------------------------------


@pytest.mark.anyio
class TestExecutionOrchestratorLifecycle:

    def _setup(self, agents=None):
        store = InMemoryExecutionStore()
        bus = EventBus(enabled=True)
        execution_id = str(uuid.uuid4())
        store.create_execution(make_record(execution_id, prompt="Write a report on AI"))
        orch = IsolatedOrchestrator(
            execution_id=execution_id,
            agents=agents or make_5_agents(),
            store=store,
            event_bus=bus,
        )
        return store, bus, execution_id, orch

    async def test_full_lifecycle_completes(self):
        store, _, execution_id, orch = self._setup()
        await orch.start_execution()
        assert store.get_execution(execution_id).status == ExecutionState.COMPLETED

    async def test_progress_reaches_one_on_completion(self):
        store, _, execution_id, orch = self._setup()
        await orch.start_execution()
        assert store.get_execution(execution_id).progress == 1.0

    async def test_timeline_has_entries(self):
        store, _, execution_id, orch = self._setup()
        await orch.start_execution()
        timeline = store.get_timeline(execution_id)
        events = [e.event for e in timeline]
        assert len(timeline) >= 4
        assert "INITIALIZING" in events
        assert "PLANNING" in events
        assert "RUNNING" in events
        assert "COMPLETED" in events

    async def test_agent_nodes_registered_in_dag(self):
        store, _, execution_id, orch = self._setup()
        await orch.start_execution()
        nodes = store.get_agent_nodes(execution_id)
        assert len(nodes) == 5
        names = {n.name for n in nodes}
        assert "PlannerAgent" in names
        assert "ReporterAgent" in names

    async def test_completed_agents_have_correct_status(self):
        store, _, execution_id, orch = self._setup()
        await orch.start_execution()
        for node in store.get_agent_nodes(execution_id):
            assert node.status == "COMPLETED", f"{node.name} should be COMPLETED, got {node.status}"

    async def test_token_accumulation(self):
        store, _, execution_id, orch = self._setup()
        await orch.start_execution()
        # 5 FastSuccessAgents × 100 tokens each = 500
        assert store.get_execution(execution_id).totalTokens == 500

    async def test_events_emitted_to_bus(self):
        received: list = []
        bus = EventBus(enabled=True)
        bus.subscribe(received.append)

        store = InMemoryExecutionStore()
        execution_id = str(uuid.uuid4())
        store.create_execution(make_record(execution_id))
        orch = IsolatedOrchestrator(
            execution_id=execution_id,
            agents=make_5_agents(),
            store=store,
            event_bus=bus,
        )
        await orch.start_execution()

        types = {type(e).__name__ for e in received}
        assert "ExecutionCreated" in types
        assert "ExecutionStarted" in types
        assert "AgentStarted" in types
        assert "AgentCompleted" in types
        assert "ExecutionCompleted" in types

    async def test_failing_agents_recorded(self):
        """Orchestrator records failed agents but continues to completion."""
        agents = [
            FastFailingAgent("PlannerAgent"),
            FastFailingAgent("ResearchAgent"),
            FastFailingAgent("ReasoningAgent"),
            FastSuccessAgent("ValidationAgent"),
            FastSuccessAgent("ReporterAgent"),
        ]
        store, _, execution_id, orch = self._setup(agents=agents)
        await orch.start_execution()
        record = store.get_execution(execution_id)
        assert record.status in (ExecutionState.COMPLETED, ExecutionState.FAILED)
        assert record.failedAgentCount >= 1


# ---------------------------------------------------------------------------
# Cancellation tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
class TestCancellation:

    async def test_cancel_before_execution_sets_cancelled(self):
        store = InMemoryExecutionStore()
        bus = EventBus(enabled=True)
        execution_id = str(uuid.uuid4())
        store.create_execution(make_record(execution_id))

        orch = IsolatedOrchestrator(
            execution_id=execution_id,
            agents=make_5_agents(),
            store=store,
            event_bus=bus,
        )
        orch.request_cancel()

        with pytest.raises(asyncio.CancelledError):
            await orch.start_execution()

        assert store.get_execution(execution_id).status == ExecutionState.CANCELLED


# ---------------------------------------------------------------------------
# ExecutionScheduler tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
class TestExecutionScheduler:

    async def test_scheduler_starts_and_stops(self):
        scheduler = ExecutionScheduler(max_concurrent=1)
        await scheduler.start()
        assert scheduler._running is True
        await scheduler.stop()
        assert scheduler._running is False

    async def test_scheduler_queue_depth(self):
        scheduler = ExecutionScheduler(max_concurrent=1)
        # Initialise queue without starting the worker loop
        scheduler._queue = asyncio.Queue()
        await scheduler._queue.put("a")
        await scheduler._queue.put("b")
        assert scheduler.queue_depth == 2

    async def test_scheduler_processes_execution(self):
        """End-to-end: scheduler dispatches an execution to COMPLETED."""
        from core.execution_store import get_execution_store
        store = get_execution_store()

        execution_id = str(uuid.uuid4())
        store.create_execution(make_record(execution_id, prompt="Scheduler integration test"))

        scheduler = ExecutionScheduler(max_concurrent=1)
        await scheduler.start()
        await scheduler.enqueue(execution_id)

        deadline = time.time() + 20.0
        while time.time() < deadline:
            await asyncio.sleep(0.3)
            r = store.get_execution(execution_id)
            if r and r.status in (ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED):
                break

        await scheduler.stop()

        final = store.get_execution(execution_id)
        assert final is not None
        assert final.status == ExecutionState.COMPLETED


# ---------------------------------------------------------------------------
# Store timeline tests (synchronous)
# ---------------------------------------------------------------------------


class TestStoreTimeline:

    def test_append_and_get_timeline(self):
        from schemas.execution import TimelineEntry
        store = InMemoryExecutionStore()
        execution_id = str(uuid.uuid4())
        store.create_execution(make_record(execution_id))

        entry = TimelineEntry(timestamp=time.time(), event="INITIALIZING", detail="test")
        store.append_timeline_entry(execution_id, entry)
        timeline = store.get_timeline(execution_id)
        assert len(timeline) == 1
        assert timeline[0].event == "INITIALIZING"

    def test_timeline_synced_on_record(self):
        from schemas.execution import TimelineEntry
        store = InMemoryExecutionStore()
        execution_id = str(uuid.uuid4())
        store.create_execution(make_record(execution_id))

        for i in range(3):
            store.append_timeline_entry(
                execution_id,
                TimelineEntry(timestamp=time.time(), event=f"event_{i}", detail="")
            )

        record = store.get_execution(execution_id)
        assert len(record.timeline) == 3

    def test_empty_timeline_returns_empty_list(self):
        store = InMemoryExecutionStore()
        assert store.get_timeline("nonexistent") == []
