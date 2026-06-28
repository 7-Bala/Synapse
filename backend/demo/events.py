"""Frontend presentation layer event schemas."""

from typing import Dict, List, Literal

from pydantic import BaseModel


class BaseFrontendEvent(BaseModel):
    """Base event contract for the React frontend."""

    timestamp_ms: int
    evidence_cycle: int
    event_type: str


class EvidenceReceivedEvent(BaseFrontendEvent):
    """Emitted when new evidence arrives in a cycle."""

    event_type: Literal["EvidenceReceived"] = "EvidenceReceived"
    payload: List[Dict[str, str]]


class SpecialistCompletedEvent(BaseFrontendEvent):
    """Emitted when a specialist completes its analysis."""

    event_type: Literal["SpecialistCompleted"] = "SpecialistCompleted"
    specialist: str
    confidence: float
    findings: str


class ConsensusUpdatedEvent(BaseFrontendEvent):
    """Emitted when the Consensus Specialist makes a final decision."""

    event_type: Literal["ConsensusUpdated"] = "ConsensusUpdated"
    decision: str
    confidence: float
    human_review_required: bool


class DownstreamSystemsUpdatedEvent(BaseFrontendEvent):
    """Emitted when enterprise downstream systems react to consensus."""

    event_type: Literal["DownstreamSystemsUpdated"] = "DownstreamSystemsUpdated"
    systems: List[Dict[str, str]]
