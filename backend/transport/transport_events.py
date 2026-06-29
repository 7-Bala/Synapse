"""Canonical transport event models mapping to the shared domain model."""

from datetime import datetime, timezone
from typing import Any, Dict, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

T = TypeVar("T")


class EventEnvelope(BaseModel, Generic[T]):
    """Standard envelope for all transport events."""
    id: UUID = Field(default_factory=uuid4)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    executionId: str
    type: str
    version: int = Field(default=1)
    payload: T


class ExecutionStarted(BaseModel):
    metadata: Dict[str, Any]

class ExecutionPaused(BaseModel):
    reason: str

class ExecutionResumed(BaseModel):
    pass

class ExecutionFinished(BaseModel):
    finalOutput: Any

class ExecutionFailed(BaseModel):
    error: str

class TickStarted(BaseModel):
    tickId: int

class TickCompleted(BaseModel):
    tickId: int

class NodeStarted(BaseModel):
    nodeId: str
    agentName: str

class NodeCompleted(BaseModel):
    nodeId: str
    agentName: str
    output: Any

class ValidatorBlocked(BaseModel):
    validatorId: str
    reason: str

class ValidatorOverridden(BaseModel):
    validatorId: str
    overriddenBy: str

class BlackboardUpdated(BaseModel):
    tickId: int
    diff: Any

class ConsensusReached(BaseModel):
    consensusResult: Any

class ReplayLoaded(BaseModel):
    replayId: str

class ToolCallExecuted(BaseModel):
    toolCallId: str
    result: Any

class EvidenceDiscovered(BaseModel):
    evidenceId: str
