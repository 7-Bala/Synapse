"""Demo recorder to track the chronological execution of the pipeline."""

from datetime import datetime
from typing import Any, Dict, List, Optional

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
        self, cycle_id: int, evidence_list: List[Evidence]
    ) -> None:
        """Logs the arrival of new evidence."""
        self.events.append(
            {
                "timestamp": datetime.now().isoformat(),
                "type": "evidence_arrival",
                "evidence_cycle": cycle_id,
                "data": [
                    {"id": str(e.id), "content": e.content, "source": e.source}
                    for e in evidence_list
                ],
            }
        )

    def record_agent_completion(self, cycle_id: int, agent_output: AgentOutput) -> None:
        """Logs when a specialist completes its processing."""
        specialist_name = agent_output.agent_name.replace("Agent", " Specialist")
        self.events.append(
            {
                "timestamp": datetime.now().isoformat(),
                "type": "specialist_completion",
                "evidence_cycle": cycle_id,
                "specialist": specialist_name,
                "confidence": agent_output.confidence,
                "findings": agent_output.findings,
            }
        )

    def record_consensus_update(
        self,
        cycle_id: int,
        consensus: ConsensusOutput,
        downstream_states: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """Logs the final consensus update for a cycle."""
        self.events.append(
            {
                "timestamp": datetime.now().isoformat(),
                "type": "consensus_update",
                "evidence_cycle": cycle_id,
                "decision": consensus.decision,
                "confidence": consensus.confidence,
                "downstream_systems": downstream_states or [],
            }
        )

        self.decision_timeline.append(
            {
                "evidence_cycle": cycle_id,
                "decision": consensus.decision,
                "confidence": consensus.confidence,
                "human_review_required": consensus.human_review_required,
                "downstream_systems": downstream_states or [],
            }
        )
