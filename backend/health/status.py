"""Health status definitions."""

from enum import Enum


class HealthStatus(str, Enum):
    """Deterministic health status values for infrastructure components."""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
