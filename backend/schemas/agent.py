"""Agent output schemas for the Synapse backend."""

from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class AgentOutput(BaseModel):
    """Represents the structured output from a single agent tick.
    Used by stub agents and the orchestrator layer.
    """

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


class SpecialistStatus(str, Enum):
    """Valid status enums for live specialists."""

    COMPLETE = "COMPLETE"
    UNCERTAIN = "UNCERTAIN"
    FAILED = "FAILED"


class LiveSpecialistOutput(BaseModel):
    """Canonical uniform schema for all live Cerebras specialists."""

    specialist: str = Field(..., description="Name of the specialist")
    status: SpecialistStatus = Field(
        ..., description="Status of the specialist reasoning"
    )
    finding: str = Field(..., description="Core finding of the specialist")
    reasoning: str = Field(..., description="Detailed reasoning process")
    confidence_reason: str = Field(
        ..., description="Qualitative explanation for confidence"
    )
    citations: List[str] = Field(
        default_factory=list, description="List of evidence IDs or sources cited"
    )
    latency_ms: int = Field(0, description="Latency of the LLM call in milliseconds")
    tokens_in: int = Field(0, description="Prompt tokens used")
    tokens_out: int = Field(0, description="Completion tokens used")
    prompt_version: str = Field(..., description="Version of the prompt used")
    cache_hit: bool = Field(
        False, description="Whether the response was loaded from cache"
    )
