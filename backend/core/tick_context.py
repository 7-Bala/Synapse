"""TickContext implementation for the Synapse backend."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from schemas.blackboard import BlackboardEntry
from schemas.consensus import ConsensusOutput
from schemas.evidence import Evidence


class TickContext(BaseModel):
    """Immutable context passed to all agents during a tick."""

    model_config = ConfigDict(frozen=True)

    tick_id: int = Field(..., description="The current tick identifier")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When the tick started"
    )
    evidence_delta: List[Evidence] = Field(
        ..., description="New evidence introduced in this tick"
    )
    blackboard_snapshot: List[BlackboardEntry] = Field(
        ..., description="Snapshot of the blackboard at start of tick"
    )
    previous_consensus: Optional[ConsensusOutput] = Field(
        None, description="Consensus output from the previous tick"
    )
