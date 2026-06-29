"""Health models for operational monitoring."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field

from health.status import HealthStatus


class ComponentHealth(BaseModel):
    """Health information for a specific infrastructure component."""

    name: str
    status: HealthStatus
    message: str
    timestamp: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SystemHealth(BaseModel):
    """Overall health of the Synapse infrastructure."""

    overall_status: HealthStatus
    generated_at: str
    components: Dict[str, ComponentHealth] = Field(default_factory=dict)


class InfrastructureFailure(BaseModel):
    """Represents a specific failure in the infrastructure."""

    timestamp: str
    component: str
    error_type: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)


class FailureReport(BaseModel):
    """Report detailing infrastructure failures."""

    generated_at: str
    total_failures: int
    failures: List[InfrastructureFailure] = Field(default_factory=list)


class RecoveryEvent(BaseModel):
    """Represents a recovery action taken by the RecoveryManager."""

    timestamp: str
    replay_id: str
    action: str
    success: bool
    details: Dict[str, Any] = Field(default_factory=dict)


class RecoveryReport(BaseModel):
    """Report detailing recovery manager statistics."""

    generated_at: str
    total_recoveries: int
    successful_recoveries: int
    failed_recoveries: int
    events: List[RecoveryEvent] = Field(default_factory=list)


class ProcessMetrics(BaseModel):
    cpu_percent: float
    cpu_time_seconds: float
    rss_memory_mb: float
    vms_memory_mb: float
    thread_count: int
    open_file_count: int
    process_uptime_seconds: float
    pid: int
    psutil_available: bool


class FilesystemMetrics(BaseModel):
    artifacts_size_bytes: int
    archive_size_bytes: int
    cache_size_bytes: int
    disk_available_bytes: int
    disk_total_bytes: int
    disk_utilization_percent: float


class RuntimeMetrics(BaseModel):
    python_version: str
    platform: str
    hostname: str
    executable: str
    working_directory: str
    operating_system: str
    architecture: str


class CacheMetrics(BaseModel):
    entry_count: int
    cache_size_bytes: int
    hit_ratio: float
    miss_ratio: float
    corruption_count: int
    cleanup_count: int
    expired_entry_count: int


class EventBusMetrics(BaseModel):
    subscriber_count: int
    emitted_event_count: int
    dropped_event_count: int
    queue_size: int
    processing_rate_per_sec: float


class CircuitBreakerMetrics(BaseModel):
    state: str
    failure_count: int
    recovery_count: int
    rejection_count: int
    transition_count: int
    uptime_seconds: float


class RetryMetrics(BaseModel):
    retry_attempts: int
    retry_successes: int
    retry_failures: int
    exhausted_retries: int
    average_retry_delay_ms: float


class ResourceViolation(BaseModel):
    metric: str
    value: float
    threshold: float
    level: HealthStatus
    message: str


class ResourceReport(BaseModel):
    """Report detailing resource and storage statistics."""

    generated_at: str
    overall_status: HealthStatus
    process: ProcessMetrics
    filesystem: FilesystemMetrics
    runtime: RuntimeMetrics
    cache: CacheMetrics
    event_bus: EventBusMetrics
    circuit_breakers: Dict[str, CircuitBreakerMetrics]
    retry_policy: RetryMetrics
    violations: List[ResourceViolation] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
