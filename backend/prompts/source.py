"""Schemas and prompt configurations for the Source agent."""

from pydantic import BaseModel, Field


class SourceResponse(BaseModel):
    """The expected JSON structure from the Cerebras model for SourceAgent."""

    findings: str = Field(
        ..., description="Detailed findings about the source reliability"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0"
    )
    is_reliable: bool = Field(
        ..., description="Whether the source is considered reliable"
    )
