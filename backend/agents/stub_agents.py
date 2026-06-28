"""Stub agent implementations for Synapse Sprint 1."""

import asyncio

from agents.base import BaseAgent
from core.tick_context import TickContext
from schemas.agent import AgentOutput


class StubAgent(BaseAgent):
    """A generic stub agent that returns a configured deterministic output."""

    def __init__(
        self,
        agent_name: str,
        findings: str,
        confidence: float = 0.9,
        delay_seconds: float = 0.0,
    ):
        """Initializes the stub agent.

        Args:
            agent_name: The name of the agent.
            findings: The deterministic findings to return.
            confidence: The deterministic confidence score.
            delay_seconds: Optional delay to simulate processing time.
        """
        self._name = agent_name
        self._findings = findings
        self._confidence = confidence
        self._delay_seconds = delay_seconds

    @property
    def name(self) -> str:
        """Returns the configured agent name."""
        return self._name

    async def run(self, context: TickContext) -> AgentOutput:
        """Simulates agent execution and returns deterministic output."""
        if self._delay_seconds > 0:
            await asyncio.sleep(self._delay_seconds)

        return AgentOutput(
            agent_name=self.name, confidence=self._confidence, findings=self._findings
        )


def create_vision_agent() -> BaseAgent:
    """Creates a stub VisionAgent."""
    return StubAgent(
        agent_name="VisionAgent", findings="No objects detected in the current view."
    )


def create_source_agent() -> BaseAgent:
    """Creates a stub SourceAgent."""
    return StubAgent(
        agent_name="SourceAgent", findings="Source verified as reliable system input."
    )


def create_timeline_agent() -> BaseAgent:
    """Creates a stub TimelineAgent."""
    return StubAgent(
        agent_name="TimelineAgent", findings="Event occurred in chronological sequence."
    )


def create_contradiction_agent() -> BaseAgent:
    """Creates a stub ContradictionAgent."""
    return StubAgent(
        agent_name="ContradictionAgent",
        findings="No contradictions found in current evidence delta.",
    )


def create_prediction_agent() -> BaseAgent:
    """Creates a stub PredictionAgent."""
    return StubAgent(
        agent_name="PredictionAgent", findings="System state expected to remain stable."
    )


def create_consensus_agent() -> BaseAgent:
    """Creates a stub ConsensusAgent.

    Note: The actual Consensus operation is typically handled by the Orchestrator,
    but this provides a stub agent if it is treated as a standard agent in the pipeline.
    """
    return StubAgent(
        agent_name="ConsensusAgent", findings="All agents agree on the current state."
    )
