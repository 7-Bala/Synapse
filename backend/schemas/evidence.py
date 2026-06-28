"""Evidence schema for the Synapse backend."""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Evidence(BaseModel):
    """Represents a piece of evidence injected into the system."""

    model_config = ConfigDict(frozen=True)

    id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for the evidence"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When the evidence was generated"
    )
    content: str = Field(..., description="The actual evidence data")
    source: str = Field(..., description="The origin of this evidence")
