"""Demo recorder to track the chronological execution of the pipeline."""

import json
from typing import Dict, List, Optional

from demo.events import (
    BaseFrontendEvent,
    ConsensusUpdatedEvent,
    DownstreamSystemsUpdatedEvent,
    EvidenceReceivedEvent,
    SpecialistCompletedEvent,
)
from schemas.agent import AgentOutput
from schemas.consensus import ConsensusOutput
from schemas.evidence import Evidence


class DemoRecorder:
    """Records events chronologically for playback and frontend usage."""

    def __init__(self) -> None:
        """Initializes the recorder."""
        self.events: List[BaseFrontendEvent] = []
        self._mock_time_ms = 0

    def _next_time(self) -> int:
        """Returns a deterministic monotonic timestamp."""
        self._mock_time_ms += 10
        return self._mock_time_ms

    def record_evidence_arrival(
        self, cycle_id: int, evidence_list: List[Evidence]
    ) -> None:
        """Logs the arrival of new evidence."""
        payload = [
            {"id": str(e.id), "content": e.content, "source": e.source}
            for e in evidence_list
        ]
        event = EvidenceReceivedEvent(
            timestamp_ms=self._next_time(),
            evidence_cycle=cycle_id,
            payload=payload,
        )
        self.events.append(event)

    def record_agent_completion(self, cycle_id: int, agent_output: AgentOutput) -> None:
        """Logs when a specialist completes its processing."""
        specialist_name = agent_output.agent_name.replace("Agent", " Specialist")
        event = SpecialistCompletedEvent(
            timestamp_ms=self._next_time(),
            evidence_cycle=cycle_id,
            specialist=specialist_name,
            confidence=agent_output.confidence,
            findings=agent_output.findings,
        )
        self.events.append(event)

    def record_consensus_update(
        self,
        cycle_id: int,
        consensus: ConsensusOutput,
        downstream_states: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """Logs the final consensus update for a cycle."""
        consensus_event = ConsensusUpdatedEvent(
            timestamp_ms=self._next_time(),
            evidence_cycle=cycle_id,
            decision=consensus.decision,
            confidence=consensus.confidence,
            human_review_required=consensus.human_review_required,
        )
        self.events.append(consensus_event)

        if downstream_states:
            downstream_event = DownstreamSystemsUpdatedEvent(
                timestamp_ms=self._next_time(),
                evidence_cycle=cycle_id,
                systems=downstream_states,
            )
            self.events.append(downstream_event)

    def export_timeline(self, filepath: str) -> None:
        """Exports the event timeline to a deterministic JSON file."""
        # Sort events deterministically to ensure stable output regardless of async completion order
        # Sort by: cycle_id, then type priority (Evidence -> Specialist -> Consensus -> Downstream), then specialist name.

        type_priority = {
            "EvidenceReceived": 1,
            "SpecialistCompleted": 2,
            "ConsensusUpdated": 3,
            "DownstreamSystemsUpdated": 4,
        }

        def sort_key(e: BaseFrontendEvent):
            spec_name = getattr(e, "specialist", "")
            return (e.evidence_cycle, type_priority.get(e.event_type, 99), spec_name)

        sorted_events = sorted(self.events, key=sort_key)

        # Rewrite timestamps after sorting to ensure strictly monotonically increasing times in the final log
        final_time = 0
        for ev in sorted_events:
            final_time += 10
            ev.timestamp_ms = final_time

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([e.model_dump() for e in sorted_events], f, indent=2)
