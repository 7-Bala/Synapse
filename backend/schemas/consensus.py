"""Consensus schemas for the Synapse backend."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConsensusOutput(BaseModel):
    """Represents the final decision reached by the consensus process."""

    model_config = ConfigDict(frozen=True)

    decision: str = Field(..., description="The final consensus decision")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Overall confidence in the decision"
    )
    explanation: str = Field(
        ..., description="Explanation or reasoning for the decision"
    )
    human_review_required: bool = Field(
        default=False, description="Whether human review is required"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When consensus was reached"
    )
