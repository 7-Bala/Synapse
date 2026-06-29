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
    cache_key: str
    provider: str
    cache_version: str
    schema_version: str
    ttl: int
    checksum: Optional[str] = None


class CacheMiss(BaseEvent):
    cache_key: str
    provider: str
    cache_version: str
    schema_version: str
    ttl: int
    checksum: Optional[str] = None


class CacheWrite(BaseEvent):
    cache_key: str
    provider: str
    cache_version: str
    schema_version: str
    ttl: int
    checksum: Optional[str] = None


class CacheDelete(BaseEvent):
    cache_key: str
    provider: str
    cache_version: str
    schema_version: str
    ttl: int
    checksum: Optional[str] = None


class CacheExpired(BaseEvent):
    cache_key: str
    provider: str
    cache_version: str
    schema_version: str
    ttl: int
    checksum: Optional[str] = None


class CacheCorrupted(BaseEvent):
    cache_key: str
    provider: str
    cache_version: str
    schema_version: str
    ttl: int
    checksum: Optional[str] = None


class CacheRecovered(BaseEvent):
    cache_key: str
    provider: str
    cache_version: str
    schema_version: str
    ttl: int
    checksum: Optional[str] = None


class CacheCleanupStarted(BaseEvent):
    provider: str


class CacheCleanupFinished(BaseEvent):
    provider: str
    entries_removed: int


class ValidationStarted(BaseEvent):
    pass


class ValidationFinished(BaseEvent):
    success: bool


class ArtifactGenerated(BaseEvent):
    artifact_type: str
    file_path: str


class ReplayValidated(BaseEvent):
    success: bool


class RetryStarted(BaseEvent):
    attempt: int


class RetryAttempt(BaseEvent):
    attempt: int
    delay_ms: float
    error: str
    duration_ms: float


class RetrySucceeded(BaseEvent):
    attempt: int
    duration_ms: float


class RetryFailedTerminal(BaseEvent):
    attempt: int
    error: str
    duration_ms: float


class RetryExhausted(BaseEvent):
    attempt: int
    error: str
    duration_ms: float


class CircuitOpened(BaseEvent):
    dependency: str
    reason: str


class CircuitClosed(BaseEvent):
    dependency: str


class CircuitHalfOpen(BaseEvent):
    dependency: str


class CircuitRejected(BaseEvent):
    dependency: str


class CircuitFailure(BaseEvent):
    dependency: str
    error: str


class CircuitRecovered(BaseEvent):
    dependency: str


# --- Failure Injection Events ---


class FailureScenarioStarted(BaseEvent):
    """Emitted when a failure injection scenario begins."""

    scenario_name: str
    profile_name: str
    fault_count: int


class FailureScenarioCompleted(BaseEvent):
    """Emitted when a failure injection scenario ends."""

    scenario_name: str
    profile_name: str
    injected_count: int
    recovered_count: int
    duration_ms: float


class FailureInjected(BaseEvent):
    """Emitted when a fault is actively injected into a component."""

    component: str
    fault_type: str
    occurrence: int


class FailureRecovered(BaseEvent):
    """Emitted when a component recovers after an injected failure."""

    component: str
    fault_type: str


class FailureIgnored(BaseEvent):
    """Emitted when a fault was configured but not triggered (e.g., count exhausted)."""

    component: str
    fault_type: str
    reason: str


class FailureBypassed(BaseEvent):
    """Emitted when injection is disabled and a component bypasses the injector."""

    component: str
    fault_type: str
