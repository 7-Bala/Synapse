"""Mock specialist agents for exercising the Synapse Orchestrator Runtime.

These agents simulate realistic latency, token usage, confidence scores, and
a configurable failure rate (default 5%). They use no external LLM APIs.

Available agents:
  PlannerAgent   — Decomposes user prompt into an ordered subtask plan.
  ResearchAgent  — Synthesizes relevant context from available evidence.
  ReasoningAgent — Applies domain logic and inference to the research.
  ValidationAgent — Validates outputs for consistency and correctness.
  ReporterAgent  — Assembles the final structured deliverable.
"""

import asyncio
import random
import time
from typing import List

from core.agents.base_agent import (
    AgentPlan,
    AgentResult,
    ExecutionContext,
    SpecialistAgent,
)


# ---------------------------------------------------------------------------
# Shared simulation helpers
# ---------------------------------------------------------------------------

def _simulate_failure(failure_rate: float) -> bool:
    """Returns True if this execution should simulate a failure."""
    return random.random() < failure_rate


# ---------------------------------------------------------------------------
# PlannerAgent
# ---------------------------------------------------------------------------


class PlannerAgent(SpecialistAgent):
    """Decomposes the user prompt into an ordered execution plan."""

    LATENCY_S = 0.8
    TOKENS = 400
    FAILURE_RATE = 0.05

    @property
    def name(self) -> str:
        return "PlannerAgent"

    @property
    def role(self) -> str:
        return "Task Decomposition & Planning"

    @property
    def model(self) -> str:
        return "mock-planner-v1"

    async def plan(self, context: ExecutionContext) -> AgentPlan:
        await asyncio.sleep(self.LATENCY_S * 0.3)
        return AgentPlan(
            agent_name=self.name,
            steps=[
                "Analyse user prompt intent",
                "Identify key research domains",
                "Define validation criteria",
                "Outline report structure",
            ],
            estimated_tokens=self.TOKENS,
            confidence=0.95,
        )

    async def execute(self, plan: AgentPlan, context: ExecutionContext) -> AgentResult:
        t0 = time.perf_counter()
        await asyncio.sleep(self.LATENCY_S * 0.7)

        if _simulate_failure(self.FAILURE_RATE):
            return AgentResult(
                agent_name=self.name,
                success=False,
                output="",
                tokens_used=50,
                latency_ms=int((time.perf_counter() - t0) * 1000),
                confidence=0.0,
                error="PlannerAgent: failed to decompose prompt — insufficient context",
            )

        return AgentResult(
            agent_name=self.name,
            success=True,
            output=f"Execution plan for: '{context.user_prompt[:80]}' — {len(plan.steps)} steps identified.",
            tokens_used=self.TOKENS,
            latency_ms=int((time.perf_counter() - t0) * 1000),
            confidence=0.95,
        )

    async def validate(self, result: AgentResult, context: ExecutionContext) -> bool:
        return result.success and len(result.output) > 0

    async def cleanup(self) -> None:
        pass


# ---------------------------------------------------------------------------
# ResearchAgent
# ---------------------------------------------------------------------------


class ResearchAgent(SpecialistAgent):
    """Fetches and synthesises relevant context from available evidence."""

    LATENCY_S = 1.2
    TOKENS = 800
    FAILURE_RATE = 0.05

    @property
    def name(self) -> str:
        return "ResearchAgent"

    @property
    def role(self) -> str:
        return "Evidence Retrieval & Synthesis"

    @property
    def model(self) -> str:
        return "mock-research-v1"

    async def plan(self, context: ExecutionContext) -> AgentPlan:
        await asyncio.sleep(self.LATENCY_S * 0.2)
        return AgentPlan(
            agent_name=self.name,
            steps=["Query knowledge base", "Retrieve top-k evidence", "Synthesise findings"],
            estimated_tokens=self.TOKENS,
            confidence=0.88,
        )

    async def execute(self, plan: AgentPlan, context: ExecutionContext) -> AgentResult:
        t0 = time.perf_counter()
        await asyncio.sleep(self.LATENCY_S * 0.8)

        if _simulate_failure(self.FAILURE_RATE):
            return AgentResult(
                agent_name=self.name,
                success=False,
                output="",
                tokens_used=100,
                latency_ms=int((time.perf_counter() - t0) * 1000),
                confidence=0.0,
                error="ResearchAgent: retrieval timeout — no evidence sources available",
            )

        return AgentResult(
            agent_name=self.name,
            success=True,
            output=(
                f"Synthesised research for '{context.user_prompt[:60]}': "
                "Found 7 relevant evidence sources. Key insights extracted across 3 domains."
            ),
            tokens_used=self.TOKENS,
            latency_ms=int((time.perf_counter() - t0) * 1000),
            confidence=0.88,
        )

    async def validate(self, result: AgentResult, context: ExecutionContext) -> bool:
        return result.success

    async def cleanup(self) -> None:
        pass


# ---------------------------------------------------------------------------
# ReasoningAgent
# ---------------------------------------------------------------------------


class ReasoningAgent(SpecialistAgent):
    """Applies domain logic and inference to research outputs."""

    LATENCY_S = 1.0
    TOKENS = 600
    FAILURE_RATE = 0.05

    @property
    def name(self) -> str:
        return "ReasoningAgent"

    @property
    def role(self) -> str:
        return "Domain Reasoning & Inference"

    @property
    def model(self) -> str:
        return "mock-reasoning-v1"

    async def plan(self, context: ExecutionContext) -> AgentPlan:
        await asyncio.sleep(self.LATENCY_S * 0.2)
        return AgentPlan(
            agent_name=self.name,
            steps=["Load research context", "Apply logical chains", "Derive conclusions"],
            estimated_tokens=self.TOKENS,
            confidence=0.91,
        )

    async def execute(self, plan: AgentPlan, context: ExecutionContext) -> AgentResult:
        t0 = time.perf_counter()
        await asyncio.sleep(self.LATENCY_S * 0.8)

        if _simulate_failure(self.FAILURE_RATE):
            return AgentResult(
                agent_name=self.name,
                success=False,
                output="",
                tokens_used=80,
                latency_ms=int((time.perf_counter() - t0) * 1000),
                confidence=0.0,
                error="ReasoningAgent: inference chain produced contradictory conclusions",
            )

        return AgentResult(
            agent_name=self.name,
            success=True,
            output=(
                "Reasoning complete: 3 primary conclusions derived with high confidence. "
                "2 competing hypotheses identified and ranked by probability."
            ),
            tokens_used=self.TOKENS,
            latency_ms=int((time.perf_counter() - t0) * 1000),
            confidence=0.91,
        )

    async def validate(self, result: AgentResult, context: ExecutionContext) -> bool:
        return result.success and result.confidence > 0.7

    async def cleanup(self) -> None:
        pass


# ---------------------------------------------------------------------------
# ValidationAgent
# ---------------------------------------------------------------------------


class ValidationAgent(SpecialistAgent):
    """Validates agent outputs for consistency and correctness."""

    LATENCY_S = 0.6
    TOKENS = 200
    FAILURE_RATE = 0.03  # Slightly lower failure rate — validation is critical path

    @property
    def name(self) -> str:
        return "ValidationAgent"

    @property
    def role(self) -> str:
        return "Output Validation & Quality Control"

    @property
    def model(self) -> str:
        return "mock-validation-v1"

    async def plan(self, context: ExecutionContext) -> AgentPlan:
        await asyncio.sleep(self.LATENCY_S * 0.2)
        return AgentPlan(
            agent_name=self.name,
            steps=["Check schema compliance", "Verify logical consistency", "Score confidence"],
            estimated_tokens=self.TOKENS,
            confidence=0.99,
        )

    async def execute(self, plan: AgentPlan, context: ExecutionContext) -> AgentResult:
        t0 = time.perf_counter()
        await asyncio.sleep(self.LATENCY_S * 0.8)

        if _simulate_failure(self.FAILURE_RATE):
            return AgentResult(
                agent_name=self.name,
                success=False,
                output="",
                tokens_used=50,
                latency_ms=int((time.perf_counter() - t0) * 1000),
                confidence=0.0,
                error="ValidationAgent: output failed consistency check — schema violation detected",
            )

        return AgentResult(
            agent_name=self.name,
            success=True,
            output="All outputs passed validation. Schema compliance: PASS. Logical consistency: PASS.",
            tokens_used=self.TOKENS,
            latency_ms=int((time.perf_counter() - t0) * 1000),
            confidence=0.99,
        )

    async def validate(self, result: AgentResult, context: ExecutionContext) -> bool:
        return result.success

    async def cleanup(self) -> None:
        pass


# ---------------------------------------------------------------------------
# ReporterAgent
# ---------------------------------------------------------------------------


class ReporterAgent(SpecialistAgent):
    """Assembles the final structured deliverable from all upstream outputs."""

    LATENCY_S = 0.5
    TOKENS = 300
    FAILURE_RATE = 0.02

    @property
    def name(self) -> str:
        return "ReporterAgent"

    @property
    def role(self) -> str:
        return "Report Assembly & Delivery"

    @property
    def model(self) -> str:
        return "mock-reporter-v1"

    async def plan(self, context: ExecutionContext) -> AgentPlan:
        await asyncio.sleep(self.LATENCY_S * 0.2)
        return AgentPlan(
            agent_name=self.name,
            steps=["Collect all outputs", "Structure report", "Format for delivery"],
            estimated_tokens=self.TOKENS,
            confidence=0.97,
        )

    async def execute(self, plan: AgentPlan, context: ExecutionContext) -> AgentResult:
        t0 = time.perf_counter()
        await asyncio.sleep(self.LATENCY_S * 0.8)

        if _simulate_failure(self.FAILURE_RATE):
            return AgentResult(
                agent_name=self.name,
                success=False,
                output="",
                tokens_used=30,
                latency_ms=int((time.perf_counter() - t0) * 1000),
                confidence=0.0,
                error="ReporterAgent: failed to assemble final report — missing upstream outputs",
            )

        return AgentResult(
            agent_name=self.name,
            success=True,
            output=(
                f"Final report assembled for: '{context.user_prompt[:60]}'. "
                "Document ready for delivery. Total: 4 sections, 2,300 words."
            ),
            tokens_used=self.TOKENS,
            latency_ms=int((time.perf_counter() - t0) * 1000),
            confidence=0.97,
        )

    async def validate(self, result: AgentResult, context: ExecutionContext) -> bool:
        return result.success

    async def cleanup(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Default agent roster for the orchestrator
# ---------------------------------------------------------------------------


def default_agent_roster() -> List[SpecialistAgent]:
    """Returns the default ordered list of specialist agents for a full execution."""
    return [
        PlannerAgent(),
        ResearchAgent(),
        ReasoningAgent(),
        ValidationAgent(),
        ReporterAgent(),
    ]
