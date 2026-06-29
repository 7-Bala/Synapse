"""Tests for the passive health monitoring subsystem."""

import json
import pytest
from unittest.mock import patch

from health.status import HealthStatus
from health.models import SystemHealth, ComponentHealth
from health.health_check import HealthMonitor
from health.reports import HealthReporter
from observability.event_bus import EventBus
from observability.events import CacheCorrupted, CircuitFailure, RetryExhausted


@pytest.fixture
def health_artifacts(tmp_path):
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()
    current_dir = artifacts_dir / "current"
    current_dir.mkdir()

    # Mock some expected files for HEALTHY state
    manifest = {
        "replay_id": "test_123",
        "schema_version": "1.0",
        "hashes": {"prompts_hash": "abc"},
    }
    with open(current_dir / "manifest.json", "w") as f:
        json.dump(manifest, f)

    eval_dir = tmp_path / "backend" / "evaluation_output"
    eval_dir.mkdir(parents=True)
    eval_rep = {
        "overall_status": "PASS",
        "timestamp": "2026",
        "golden_manifest": {"schema_version": "1.0"},
    }
    with open(eval_dir / "evaluation_report.json", "w") as f:
        json.dump(eval_rep, f)

    # Mock cache dir
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    with open(cache_dir / "dummy.json", "w") as f:
        f.write("{}")

    return tmp_path


def test_healthy_system(health_artifacts):
    artifacts_dir = health_artifacts / "artifacts"

    # Patch paths
    with patch("health.health_check.FilesystemCacheProvider") as MockCache:
        mock_provider = MockCache.return_value
        mock_provider.provider_name = "filesystem"
        mock_provider.cache_dir = health_artifacts / "cache"
        mock_provider.default_ttl = 3600

        with patch.object(HealthMonitor, "probe_evaluation") as mock_eval, patch.object(
            HealthMonitor, "probe_lock_manager"
        ) as mock_lock:
            # We must patch evaluation path since it looks for backend/evaluation_output relative to artifacts parent
            mock_eval.return_value = ComponentHealth(
                name="evaluation",
                status=HealthStatus.HEALTHY,
                message="Eval OK",
                timestamp="2026",
                metadata={"benchmark_status": "PASS"},
            )

            mock_lock.return_value = ComponentHealth(
                name="lock_manager",
                status=HealthStatus.HEALTHY,
                message="Mocked for test",
                timestamp="2026",
                metadata={},
            )
            monitor = HealthMonitor(str(artifacts_dir))
            system_health = monitor.aggregate_health()

            assert system_health.overall_status == HealthStatus.HEALTHY
            assert system_health.components["cache"].status == HealthStatus.HEALTHY
            assert system_health.components["provenance"].status == HealthStatus.HEALTHY
            assert (
                system_health.components["circuit_breaker"].status
                == HealthStatus.HEALTHY
            )
            assert system_health.components["event_bus"].status == HealthStatus.HEALTHY


def test_degraded_cache_via_events(health_artifacts):
    artifacts_dir = health_artifacts / "artifacts"

    with patch("health.health_check.FilesystemCacheProvider"):
        monitor = HealthMonitor(str(artifacts_dir))

        # Simulate cache corruption
        bus = EventBus.get_instance()
        bus.emit(
            CacheCorrupted(
                correlation_id="123",
                cache_key="test",
                provider="filesystem",
                cache_version="1.0",
                schema_version="1.0",
                ttl=3600,
            )
        )

        cache_health = monitor.probe_cache()
        assert cache_health.metadata["corruption_count"] == 1


def test_circuit_breaker_failure_events(health_artifacts):
    artifacts_dir = health_artifacts / "artifacts"
    monitor = HealthMonitor(str(artifacts_dir))

    bus = EventBus.get_instance()
    bus.emit(
        CircuitFailure(correlation_id="123", dependency="test_dep", error="Test error")
    )

    cb_health = monitor.probe_circuit_breaker()
    assert cb_health.metadata["failure_count"] == 1


def test_retry_exhaustion_events(health_artifacts):
    artifacts_dir = health_artifacts / "artifacts"
    monitor = HealthMonitor(str(artifacts_dir))

    bus = EventBus.get_instance()
    bus.emit(
        RetryExhausted(
            correlation_id="123", attempt=3, error="Exhausted", duration_ms=100.0
        )
    )

    retry_health = monitor.probe_retry_policy()
    assert retry_health.metadata["exhausted_retries"] == 1


def test_missing_lock_manager(health_artifacts):
    artifacts_dir = health_artifacts / "artifacts"
    monitor = HealthMonitor(str(artifacts_dir))

    lock_health = monitor.probe_lock_manager()
    assert lock_health.status == HealthStatus.HEALTHY
    assert lock_health.message == "Concurrent Safety phase intentionally deferred."
    assert lock_health.metadata["deferred"] is True


def test_missing_provenance(health_artifacts):
    artifacts_dir = health_artifacts / "artifacts"
    # Remove manifest
    (artifacts_dir / "current" / "manifest.json").unlink()

    monitor = HealthMonitor(str(artifacts_dir))
    prov_health = monitor.probe_provenance()
    assert prov_health.status == HealthStatus.UNKNOWN
    assert prov_health.message == "Missing provenance."


def test_deterministic_aggregation():
    monitor = HealthMonitor("/tmp/fake")

    # Mock probes to force statuses
    with patch.object(
        monitor,
        "probe_cache",
        return_value=ComponentHealth(
            name="c", status=HealthStatus.FAILED, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_circuit_breaker",
        return_value=ComponentHealth(
            name="cb", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_retry_policy",
        return_value=ComponentHealth(
            name="r", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_event_bus",
        return_value=ComponentHealth(
            name="e", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_lock_manager",
        return_value=ComponentHealth(
            name="l", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_artifact_writer",
        return_value=ComponentHealth(
            name="a", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_recovery_manager",
        return_value=ComponentHealth(
            name="rm", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_provenance",
        return_value=ComponentHealth(
            name="p", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_evaluation",
        return_value=ComponentHealth(
            name="ev", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ):

        system_health = monitor.aggregate_health()
        assert system_health.overall_status == HealthStatus.FAILED

    with patch.object(
        monitor,
        "probe_cache",
        return_value=ComponentHealth(
            name="c", status=HealthStatus.DEGRADED, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_circuit_breaker",
        return_value=ComponentHealth(
            name="cb", status=HealthStatus.UNKNOWN, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_retry_policy",
        return_value=ComponentHealth(
            name="r", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_event_bus",
        return_value=ComponentHealth(
            name="e", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_lock_manager",
        return_value=ComponentHealth(
            name="l", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_artifact_writer",
        return_value=ComponentHealth(
            name="a", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_recovery_manager",
        return_value=ComponentHealth(
            name="rm", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_provenance",
        return_value=ComponentHealth(
            name="p", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_evaluation",
        return_value=ComponentHealth(
            name="ev", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ):

        system_health = monitor.aggregate_health()
        assert system_health.overall_status == HealthStatus.DEGRADED

    with patch.object(
        monitor,
        "probe_cache",
        return_value=ComponentHealth(
            name="c", status=HealthStatus.UNKNOWN, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_circuit_breaker",
        return_value=ComponentHealth(
            name="cb", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_retry_policy",
        return_value=ComponentHealth(
            name="r", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_event_bus",
        return_value=ComponentHealth(
            name="e", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_lock_manager",
        return_value=ComponentHealth(
            name="l", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_artifact_writer",
        return_value=ComponentHealth(
            name="a", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_recovery_manager",
        return_value=ComponentHealth(
            name="rm", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_provenance",
        return_value=ComponentHealth(
            name="p", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ), patch.object(
        monitor,
        "probe_evaluation",
        return_value=ComponentHealth(
            name="ev", status=HealthStatus.HEALTHY, message="", timestamp=""
        ),
    ):

        system_health = monitor.aggregate_health()
        assert system_health.overall_status == HealthStatus.UNKNOWN


def test_json_schema_validation(health_artifacts):
    artifacts_dir = health_artifacts / "artifacts"
    reporter = HealthReporter(str(artifacts_dir))

    with patch.object(
        reporter.monitor,
        "aggregate_health",
        return_value=SystemHealth(
            overall_status=HealthStatus.HEALTHY, generated_at="2026", components={}
        ),
    ):
        reporter.generate_all_reports()

        # Verify JSON is generated and parseable
        with open(artifacts_dir / "current" / "health_report.json") as f:
            health_json = json.load(f)
            assert "overall_status" in health_json

        with open(artifacts_dir / "current" / "failure_report.json") as f:
            failure_json = json.load(f)
            assert "failures" in failure_json

        with open(artifacts_dir / "current" / "recovery_report.json") as f:
            recovery_json = json.load(f)
            assert "total_recoveries" in recovery_json

            with open(artifacts_dir / "current" / "resource_report.json") as f:
                resource_json = json.load(f)
                assert "filesystem" in resource_json
                assert "cache_size_bytes" in resource_json["filesystem"]


def test_historical_archive(health_artifacts):
    artifacts_dir = health_artifacts / "artifacts"
    reporter = HealthReporter(str(artifacts_dir))

    with patch.object(
        reporter.monitor,
        "aggregate_health",
        return_value=SystemHealth(
            overall_status=HealthStatus.HEALTHY, generated_at="2026", components={}
        ),
    ):
        reporter.generate_all_reports()
        reporter.archive_snapshot()

        archive_health_dir = artifacts_dir / "archive" / "health"
        assert archive_health_dir.exists()

        snapshots = list(archive_health_dir.iterdir())
        assert len(snapshots) == 1

        snapshot = snapshots[0]
        assert (snapshot / "health_report.json").exists()
        assert (snapshot / "failure_report.json").exists()
        assert (snapshot / "recovery_report.json").exists()
        assert (snapshot / "resource_report.json").exists()
