"""Tests for the passive resource monitoring subsystem."""

import json
import pytest
from unittest.mock import patch

from health.status import HealthStatus
from health.models import (
    ProcessMetrics,
)
from health.resource_monitor import ResourceMonitor
from health.reports import HealthReporter
from config.settings import settings
from observability.event_bus import EventBus
from observability.events import (
    CacheHit,
    CacheMiss,
    CircuitOpened,
    CircuitClosed,
    RetryAttempt,
)


@pytest.fixture
def resource_artifacts(tmp_path):
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()
    current_dir = artifacts_dir / "current"
    current_dir.mkdir()

    # Mock cache dir
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    with open(cache_dir / "dummy.json", "w") as f:
        f.write("{}")

    return tmp_path


def test_healthy_resource_usage(resource_artifacts):
    artifacts_dir = resource_artifacts / "artifacts"
    monitor = ResourceMonitor(str(artifacts_dir))

    proc = monitor.get_process_metrics()
    assert proc.cpu_percent >= 0.0
    assert proc.rss_memory_mb >= 0.0

    fs = monitor.get_filesystem_metrics()
    assert fs.disk_utilization_percent >= 0.0

    run = monitor.get_runtime_metrics()
    assert run.python_version != ""

    # Evaluate thresholds
    with patch.object(settings, "resource_cpu_warning", 99.0), patch.object(
        settings, "resource_memory_warning", 99999.0
    ), patch.object(settings, "resource_disk_warning", 99.0):
        violations = monitor.evaluate_thresholds(proc, fs)
        assert len(violations) == 0
        assert monitor.aggregate_status(violations) == HealthStatus.HEALTHY


def test_high_cpu_violation(resource_artifacts):
    artifacts_dir = resource_artifacts / "artifacts"
    monitor = ResourceMonitor(str(artifacts_dir))

    proc = ProcessMetrics(
        cpu_percent=95.0,
        cpu_time_seconds=10.0,
        rss_memory_mb=10.0,
        vms_memory_mb=10.0,
        thread_count=1,
        open_file_count=1,
        process_uptime_seconds=10.0,
        pid=123,
        psutil_available=True,
    )
    fs = monitor.get_filesystem_metrics()

    violations = monitor.evaluate_thresholds(proc, fs)
    assert any(v.metric == "cpu_percent" for v in violations)
    assert monitor.aggregate_status(violations) == HealthStatus.FAILED


def test_missing_psutil(resource_artifacts):
    artifacts_dir = resource_artifacts / "artifacts"

    with patch("health.resource_monitor.PSUTIL_AVAILABLE", False):
        monitor = ResourceMonitor(str(artifacts_dir))
        proc = monitor.get_process_metrics()
        assert proc.psutil_available is False
        assert proc.cpu_percent == 0.0


def test_cache_metrics(resource_artifacts):
    artifacts_dir = resource_artifacts / "artifacts"
    monitor = ResourceMonitor(str(artifacts_dir))

    bus = EventBus.get_instance()
    bus.emit(
        CacheHit(
            correlation_id="1",
            cache_key="k1",
            provider="filesystem",
            cache_version="1",
            schema_version="1",
            ttl=3600,
        )
    )
    bus.emit(
        CacheMiss(
            correlation_id="2",
            cache_key="k2",
            provider="filesystem",
            cache_version="1",
            schema_version="1",
            ttl=3600,
        )
    )

    cache = monitor.get_cache_metrics()
    assert cache.hit_ratio == 0.5
    assert cache.miss_ratio == 0.5


def test_circuit_breaker_metrics(resource_artifacts):
    artifacts_dir = resource_artifacts / "artifacts"
    monitor = ResourceMonitor(str(artifacts_dir))

    bus = EventBus.get_instance()
    bus.emit(CircuitOpened(correlation_id="1", dependency="dep1", reason="timeout"))

    cbs = monitor.get_circuit_breaker_metrics()
    assert "dep1" in cbs
    assert cbs["dep1"].state == "OPEN"
    assert cbs["dep1"].transition_count == 1

    bus.emit(CircuitClosed(correlation_id="2", dependency="dep1"))
    cbs = monitor.get_circuit_breaker_metrics()
    assert cbs["dep1"].state == "CLOSED"
    assert cbs["dep1"].transition_count == 2


def test_retry_metrics(resource_artifacts):
    artifacts_dir = resource_artifacts / "artifacts"
    monitor = ResourceMonitor(str(artifacts_dir))

    bus = EventBus.get_instance()
    bus.emit(
        RetryAttempt(
            correlation_id="1", attempt=1, delay_ms=100.0, error="err", duration_ms=10.0
        )
    )
    bus.emit(
        RetryAttempt(
            correlation_id="2", attempt=2, delay_ms=200.0, error="err", duration_ms=10.0
        )
    )

    rm = monitor.get_retry_metrics()
    assert rm.retry_attempts == 2
    assert rm.average_retry_delay_ms == 150.0


def test_report_schema_validation(resource_artifacts):
    artifacts_dir = resource_artifacts / "artifacts"
    reporter = HealthReporter(str(artifacts_dir))

    with patch.object(reporter.monitor, "aggregate_health"):
        reporter.generate_resource_report("2026")

        with open(artifacts_dir / "current" / "resource_report.json") as f:
            data = json.load(f)
            assert "process" in data
            assert "filesystem" in data
            assert "runtime" in data
            assert "cache" in data
            assert "event_bus" in data
            assert "circuit_breakers" in data
            assert "retry_policy" in data
            assert "violations" in data
            assert "overall_status" in data
