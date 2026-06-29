"""Passive resource monitoring for the Synapse infrastructure."""

import os
import sys
import time
import platform
import shutil
from pathlib import Path
from typing import Dict, Any, List

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from health.status import HealthStatus
from health.models import (
    ProcessMetrics,
    FilesystemMetrics,
    RuntimeMetrics,
    CacheMetrics,
    EventBusMetrics,
    CircuitBreakerMetrics,
    RetryMetrics,
    ResourceViolation,
)
from observability.event_bus import EventBus
from observability.events import (
    CacheHit,
    CacheMiss,
    CacheExpired,
    CacheCorrupted,
    CacheCleanupFinished,
    RetryAttempt,
    RetrySucceeded,
    RetryFailedTerminal,
    RetryExhausted,
    CircuitOpened,
    CircuitClosed,
    CircuitHalfOpen,
    CircuitRejected,
    CircuitFailure,
    CircuitRecovered,
    BaseEvent,
)
from config.settings import settings


class ResourceMonitor:
    """Passively collects resource metrics without influencing execution."""

    def __init__(self, artifacts_dir: str):
        self.artifacts_dir = Path(artifacts_dir)
        self.base_dir = self.artifacts_dir.parent
        self.cache_dir = self.base_dir / "cache"
        self.archive_dir = self.artifacts_dir / "archive"

        # Event Tracking State
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_corruptions = 0
        self.cache_cleanups = 0
        self.cache_expired = 0

        self.retry_attempts = 0
        self.retry_successes = 0
        self.retry_failures = 0
        self.retry_exhausted = 0
        self.retry_delays_ms: List[float] = []

        # Circuit Breakers state: dependency -> metrics
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}

        self.start_time = time.time()

        # Subscribe to EventBus
        self.event_bus = EventBus.get_instance()
        self._setup_subscriptions()

    def _setup_subscriptions(self) -> None:
        self.event_bus.subscribe(self._handle_event)

    def _handle_event(self, event: BaseEvent) -> None:  # noqa: C901
        if isinstance(event, CacheHit):
            self.cache_hits += 1
        elif isinstance(event, CacheMiss):
            self.cache_misses += 1
        elif isinstance(event, CacheExpired):
            self.cache_expired += 1
        elif isinstance(event, CacheCorrupted):
            self.cache_corruptions += 1
        elif isinstance(event, CacheCleanupFinished):
            self.cache_cleanups += 1
        elif isinstance(event, RetryAttempt):
            self.retry_attempts += 1
            self.retry_delays_ms.append(event.delay_ms)
        elif isinstance(event, RetrySucceeded):
            self.retry_successes += 1
        elif isinstance(event, RetryFailedTerminal):
            self.retry_failures += 1
        elif isinstance(event, RetryExhausted):
            self.retry_exhausted += 1
        elif isinstance(
            event,
            (
                CircuitOpened,
                CircuitClosed,
                CircuitHalfOpen,
                CircuitRejected,
                CircuitFailure,
                CircuitRecovered,
            ),
        ):
            dep = event.dependency
            if dep not in self.circuit_breakers:
                self.circuit_breakers[dep] = {
                    "state": "CLOSED",
                    "failure_count": 0,
                    "recovery_count": 0,
                    "rejection_count": 0,
                    "transition_count": 0,
                    "start_time": time.time(),
                }
            cb = self.circuit_breakers[dep]

            if isinstance(event, CircuitOpened):
                cb["state"] = "OPEN"
                cb["transition_count"] += 1
            elif isinstance(event, CircuitClosed):
                cb["state"] = "CLOSED"
                cb["transition_count"] += 1
            elif isinstance(event, CircuitHalfOpen):
                cb["state"] = "HALF_OPEN"
                cb["transition_count"] += 1
            elif isinstance(event, CircuitRejected):
                cb["rejection_count"] += 1
            elif isinstance(event, CircuitFailure):
                cb["failure_count"] += 1
            elif isinstance(event, CircuitRecovered):
                cb["recovery_count"] += 1

    def _get_dir_size(self, directory: Path) -> int:
        if not directory.exists():
            return 0
        return sum(f.stat().st_size for f in directory.rglob("*") if f.is_file())

    def _get_dir_entries(self, directory: Path) -> int:
        if not directory.exists():
            return 0
        return sum(1 for f in directory.rglob("*") if f.is_file())

    def get_process_metrics(self) -> ProcessMetrics:
        pid = os.getpid()
        uptime = time.time() - self.start_time

        if PSUTIL_AVAILABLE:
            try:
                proc = psutil.Process(pid)
                return ProcessMetrics(
                    cpu_percent=proc.cpu_percent(interval=0.1),
                    cpu_time_seconds=proc.cpu_times().user + proc.cpu_times().system,
                    rss_memory_mb=proc.memory_info().rss / (1024 * 1024),
                    vms_memory_mb=proc.memory_info().vms / (1024 * 1024),
                    thread_count=proc.num_threads(),
                    open_file_count=len(proc.open_files()),
                    process_uptime_seconds=uptime,
                    pid=pid,
                    psutil_available=True,
                )
            except Exception:
                pass

        # Graceful fallback
        return ProcessMetrics(
            cpu_percent=0.0,
            cpu_time_seconds=0.0,
            rss_memory_mb=0.0,
            vms_memory_mb=0.0,
            thread_count=1,
            open_file_count=0,
            process_uptime_seconds=uptime,
            pid=pid,
            psutil_available=False,
        )

    def get_filesystem_metrics(self) -> FilesystemMetrics:
        artifacts_size = self._get_dir_size(self.artifacts_dir)
        archive_size = self._get_dir_size(self.archive_dir)
        cache_size = self._get_dir_size(self.cache_dir)

        total, used, free = shutil.disk_usage(str(self.base_dir))
        utilization = (used / total) * 100 if total > 0 else 0.0

        return FilesystemMetrics(
            artifacts_size_bytes=artifacts_size,
            archive_size_bytes=archive_size,
            cache_size_bytes=cache_size,
            disk_available_bytes=free,
            disk_total_bytes=total,
            disk_utilization_percent=utilization,
        )

    def get_runtime_metrics(self) -> RuntimeMetrics:
        return RuntimeMetrics(
            python_version=sys.version.split(" ")[0],
            platform=platform.platform(),
            hostname=platform.node(),
            executable=sys.executable,
            working_directory=os.getcwd(),
            operating_system=platform.system(),
            architecture=platform.machine(),
        )

    def get_cache_metrics(self) -> CacheMetrics:
        entries = self._get_dir_entries(self.cache_dir)
        size = self._get_dir_size(self.cache_dir)

        total_requests = self.cache_hits + self.cache_misses
        hit_ratio = self.cache_hits / total_requests if total_requests > 0 else 0.0
        miss_ratio = self.cache_misses / total_requests if total_requests > 0 else 0.0

        return CacheMetrics(
            entry_count=entries,
            cache_size_bytes=size,
            hit_ratio=hit_ratio,
            miss_ratio=miss_ratio,
            corruption_count=self.cache_corruptions,
            cleanup_count=self.cache_cleanups,
            expired_entry_count=self.cache_expired,
        )

    def get_event_bus_metrics(self) -> EventBusMetrics:
        return EventBusMetrics(
            subscriber_count=len(self.event_bus._subscribers),
            emitted_event_count=self.event_bus.emitted_count,
            dropped_event_count=self.event_bus.dropped_count,
            queue_size=self.event_bus.queue_size(),
            processing_rate_per_sec=0.0,  # Optional heuristic
        )

    def get_circuit_breaker_metrics(self) -> Dict[str, CircuitBreakerMetrics]:
        res = {}
        now = time.time()
        for dep, cb in self.circuit_breakers.items():
            res[dep] = CircuitBreakerMetrics(
                state=cb["state"],
                failure_count=cb["failure_count"],
                recovery_count=cb["recovery_count"],
                rejection_count=cb["rejection_count"],
                transition_count=cb["transition_count"],
                uptime_seconds=now - cb["start_time"],
            )
        return res

    def get_retry_metrics(self) -> RetryMetrics:
        avg_delay = (
            sum(self.retry_delays_ms) / len(self.retry_delays_ms)
            if self.retry_delays_ms
            else 0.0
        )
        return RetryMetrics(
            retry_attempts=self.retry_attempts,
            retry_successes=self.retry_successes,
            retry_failures=self.retry_failures,
            exhausted_retries=self.retry_exhausted,
            average_retry_delay_ms=avg_delay,
        )

    def evaluate_thresholds(
        self, process: ProcessMetrics, fs: FilesystemMetrics
    ) -> List[ResourceViolation]:
        violations = []

        # CPU
        if process.cpu_percent > settings.resource_cpu_critical:
            violations.append(
                ResourceViolation(
                    metric="cpu_percent",
                    value=process.cpu_percent,
                    threshold=settings.resource_cpu_critical,
                    level=HealthStatus.FAILED,
                    message="CPU utilization critical.",
                )
            )
        elif process.cpu_percent > settings.resource_cpu_warning:
            violations.append(
                ResourceViolation(
                    metric="cpu_percent",
                    value=process.cpu_percent,
                    threshold=settings.resource_cpu_warning,
                    level=HealthStatus.DEGRADED,
                    message="CPU utilization warning.",
                )
            )

        # Memory
        if process.rss_memory_mb > settings.resource_memory_critical:
            violations.append(
                ResourceViolation(
                    metric="rss_memory_mb",
                    value=process.rss_memory_mb,
                    threshold=settings.resource_memory_critical,
                    level=HealthStatus.FAILED,
                    message="Memory utilization critical.",
                )
            )
        elif process.rss_memory_mb > settings.resource_memory_warning:
            violations.append(
                ResourceViolation(
                    metric="rss_memory_mb",
                    value=process.rss_memory_mb,
                    threshold=settings.resource_memory_warning,
                    level=HealthStatus.DEGRADED,
                    message="Memory utilization warning.",
                )
            )

        # Disk
        if fs.disk_utilization_percent > settings.resource_disk_critical:
            violations.append(
                ResourceViolation(
                    metric="disk_utilization_percent",
                    value=fs.disk_utilization_percent,
                    threshold=settings.resource_disk_critical,
                    level=HealthStatus.FAILED,
                    message="Disk utilization critical.",
                )
            )
        elif fs.disk_utilization_percent > settings.resource_disk_warning:
            violations.append(
                ResourceViolation(
                    metric="disk_utilization_percent",
                    value=fs.disk_utilization_percent,
                    threshold=settings.resource_disk_warning,
                    level=HealthStatus.DEGRADED,
                    message="Disk utilization warning.",
                )
            )

        return violations

    def aggregate_status(self, violations: List[ResourceViolation]) -> HealthStatus:
        if any(v.level == HealthStatus.FAILED for v in violations):
            return HealthStatus.FAILED
        if any(v.level == HealthStatus.DEGRADED for v in violations):
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY
