"""Blackboard schemas for the Synapse backend."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.agent import AgentOutput


class BlackboardEntry(BaseModel):
    """Represents a single entry stored in the blackboard."""

    model_config = ConfigDict(frozen=True)

    tick_id: int = Field(..., description="The tick ID when this entry was produced")
    agent_name: str = Field(
        ..., description="Name of the agent that produced this entry"
    )
    output: AgentOutput = Field(..., description="The output produced by the agent")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When this entry was added"
    )
