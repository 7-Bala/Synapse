"""Pipeline state management for demo generation."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set


@dataclass
class PipelineState:
    """Tracks the execution state of a replay generation."""

    scenario_name: str
    active_cycle: int = 0
    completed_specialists: Set[str] = field(default_factory=set)
    failed_specialists: Set[str] = field(default_factory=set)
    cache: Dict[str, Any] = field(default_factory=dict)
    generated_events: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
