"""Abstract SpecialistAgent interface for the Synapse Orchestrator Runtime.

Every future specialist agent must inherit from SpecialistAgent and implement
the four-phase lifecycle: plan → execute → validate → cleanup.

This module intentionally does NOT import from agents.base (the old BaseAgent)
to keep the specialist runtime decoupled from the legacy tick-based architecture.
"""

import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Execution Context — read-only view passed to every agent phase
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExecutionContext:
    """Immutable context passed to every agent lifecycle method."""

    execution_id: str
    user_prompt: str
    execution_mode: str  # LIVE | SIMULATION | REPLAY
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Structured Agent Outputs
# ---------------------------------------------------------------------------


@dataclass
class AgentPlan:
    """Output of the plan() phase."""

    agent_name: str
    steps: List[str]
    estimated_tokens: int = 0
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Output of the execute() phase."""

    agent_name: str
    success: bool
    output: str
    tokens_used: int = 0
    latency_ms: int = 0
    confidence: float = 1.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Abstract SpecialistAgent
# ---------------------------------------------------------------------------


class SpecialistAgent(abc.ABC):
    """Abstract base class for all Synapse specialist agents.

    Agents are stateless: a fresh instance is created per execution tick.
    All persistent state must be passed through ExecutionContext.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Unique identifier for this agent (used in events and DAG nodes)."""

    @property
    @abc.abstractmethod
    def role(self) -> str:
        """Human-readable role description (e.g. 'Research & Synthesis')."""

    @property
    @abc.abstractmethod
    def model(self) -> str:
        """Model identifier (e.g. 'mock-v1', 'cerebras-llama-4')."""

    @abc.abstractmethod
    async def plan(self, context: ExecutionContext) -> AgentPlan:
        """Decompose the task into discrete steps before execution.

        Args:
            context: Immutable execution context.

        Returns:
            AgentPlan: The planned steps and estimated resource usage.
        """

    @abc.abstractmethod
    async def execute(self, plan: AgentPlan, context: ExecutionContext) -> AgentResult:
        """Execute the plan produced by plan().

        Args:
            plan: The output of a prior plan() call.
            context: Immutable execution context.

        Returns:
            AgentResult: Structured output of the execution phase.
        """

    @abc.abstractmethod
    async def validate(self, result: AgentResult, context: ExecutionContext) -> bool:
        """Validate the result before it is committed.

        Args:
            result: The output of a prior execute() call.
            context: Immutable execution context.

        Returns:
            bool: True if the result is valid, False if it should be rejected.
        """

    @abc.abstractmethod
    async def cleanup(self) -> None:
        """Release any resources held during execution."""
