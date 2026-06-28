"""Agent output schemas for the Synapse backend."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentOutput(BaseModel):
    """Represents the structured output from a single agent tick."""

    model_config = ConfigDict(frozen=True)

    agent_name: str = Field(
        ..., description="Name of the agent that produced this output"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0"
    )
    findings: str = Field(
        ..., description="Structured findings or analysis from the agent"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When the output was generated"
    )
