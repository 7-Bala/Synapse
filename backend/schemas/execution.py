"""Pydantic schemas and enums representing executions and agent nodes in a DAG."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ExecutionState(str, Enum):
    QUEUED = "QUEUED"
    INITIALIZING = "INITIALIZING"
    PLANNING = "PLANNING"
    RUNNING = "RUNNING"
    VALIDATING = "VALIDATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class ExecutionMode(str, Enum):
    LIVE = "LIVE"
    SIMULATION = "SIMULATION"
    REPLAY = "REPLAY"


class TimelineEntry(BaseModel):
    """An immutable entry in the execution timeline (consumed by Replay later)."""
    timestamp: float
    event: str        # e.g. "QUEUED", "PlannerAgent.started", "COMPLETED"
    detail: str = ""
    agent: Optional[str] = None


class ExecutionRecord(BaseModel):
    id: str
    status: ExecutionState
    createdAt: float
    updatedAt: float
    startedAt: Optional[float] = None
    completedAt: Optional[float] = None
    userPrompt: str
    executionMode: ExecutionMode
    currentAgent: Optional[str] = None
    totalLatency: int = 0  # ms
    totalTokens: int = 0
    estimatedCost: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Milestone 3: timeline + runtime metrics
    timeline: List[TimelineEntry] = Field(default_factory=list)
    activeAgentCount: int = 0
    completedAgentCount: int = 0
    failedAgentCount: int = 0
    retryCount: int = 0
    progress: float = 0.0   # 0.0–1.0


class AgentNode(BaseModel):
    id: str
    name: str
    role: str
    model: str
    status: str  # IDLE, RUNNING, COMPLETED, FAILED, RETRIES
    input: Optional[str] = None
    output: Optional[str] = None
    latency: int = 0  # ms
    tokenUsage: int = 0
    confidence: float = 0.0
    retryCount: int = 0
    parentId: Optional[str] = None
    childrenIds: List[str] = Field(default_factory=list)

