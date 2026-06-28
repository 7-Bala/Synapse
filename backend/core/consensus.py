"""Lightweight consensus engine for Synapse."""

from typing import List

from schemas.agent import AgentOutput
from schemas.consensus import ConsensusOutput


def run_minimal_consensus(agent_outputs: List[AgentOutput]) -> ConsensusOutput:
    """A minimal consensus implementation that heavily weights the SourceAgent.

    This acts as a placeholder for the future advanced arbitration engine,
    but honors the exact interface expected by the system.
    """
    source_output = next(
        (out for out in agent_outputs if out.agent_name == "SourceAgent"), None
    )

    if not source_output:
        return ConsensusOutput(
            decision="No SourceAgent output available.",
            confidence=0.0,
            explanation="Consensus requires Source verification to proceed.",
            human_review_required=True,
        )

    # Minimal logic based entirely on Source confidence
    decision = (
        "Evidence Accepted" if source_output.confidence > 0.5 else "Evidence Rejected"
    )

    return ConsensusOutput(
        decision=decision,
        confidence=source_output.confidence,
        explanation=f"Based primarily on Source analysis: {source_output.findings}",
        human_review_required=(source_output.confidence < 0.7),
    )
