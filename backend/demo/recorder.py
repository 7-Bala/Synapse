"""Demo recorder to track the chronological execution of the pipeline."""

from datetime import datetime
from typing import Any, Dict, List

from schemas.agent import AgentOutput
from schemas.consensus import ConsensusOutput
from schemas.evidence import Evidence


class DemoRecorder:
    """Records events chronologically for playback and frontend usage."""

    def __init__(self) -> None:
        """Initializes the recorder."""
        self.events: List[Dict[str, Any]] = []
        self.decision_timeline: List[Dict[str, Any]] = []

    def record_evidence_arrival(
        self, tick_id: int, evidence_list: List[Evidence]
    ) -> None:
        """Logs the arrival of new evidence."""
        self.events.append(
            {
                "timestamp": datetime.now().isoformat(),
                "type": "evidence_arrival",
                "tick": tick_id,
                "data": [
                    {"id": str(e.id), "content": e.content, "source": e.source}
                    for e in evidence_list
                ],
            }
        )

    def record_agent_completion(self, tick_id: int, agent_output: AgentOutput) -> None:
        """Logs when an agent completes its processing."""
        self.events.append(
            {
                "timestamp": datetime.now().isoformat(),
                "type": "agent_completion",
                "tick": tick_id,
                "agent": agent_output.agent_name,
                "confidence": agent_output.confidence,
                "findings": agent_output.findings,
            }
        )

    def record_consensus_update(self, tick_id: int, consensus: ConsensusOutput) -> None:
        """Logs the final consensus update for a tick."""
        self.events.append(
            {
                "timestamp": datetime.now().isoformat(),
                "type": "consensus_update",
                "tick": tick_id,
                "decision": consensus.decision,
                "confidence": consensus.confidence,
            }
        )

        self.decision_timeline.append(
            {
                "tick": tick_id,
                "decision": consensus.decision,
                "confidence": consensus.confidence,
                "human_review_required": consensus.human_review_required,
            }
        )
