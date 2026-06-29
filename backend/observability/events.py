"""Strongly typed event models for Synapse observability."""

import time
from typing import Optional
from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """Base class for all observability events."""

    timestamp: float = Field(default_factory=time.time)
    correlation_id: str = Field(..., description="Tick ID or trace ID")
    specialist: Optional[str] = Field(None, description="Specialist name if applicable")


class SpecialistStarted(BaseEvent):
    evidence_cycle: int


class SpecialistFinished(BaseEvent):
    evidence_cycle: int
    status: str
    confidence: float


class LLMRequestStarted(BaseEvent):
    prompt_version: str


class LLMRequestFinished(BaseEvent):
    status: str
    tokens_in: int = 0
    tokens_out: int = 0


class CacheLookupStarted(BaseEvent):
    pass


class CacheLookupFinished(BaseEvent):
    pass


class CacheHit(BaseEvent):
    pass


class CacheMiss(BaseEvent):
    pass


class ValidationStarted(BaseEvent):
    pass


class ValidationFinished(BaseEvent):
    success: bool


class ArtifactGenerated(BaseEvent):
    artifact_type: str
    file_path: str


class ReplayValidated(BaseEvent):
    success: bool
