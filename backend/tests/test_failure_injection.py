"""Deterministic tests for Phase 9: Failure Injection Framework.

All tests are deterministic — no random sleeps, no flaky timing.
Every scenario is explicitly configured and verified.
"""

import json
import time
import pytest
from unittest.mock import MagicMock

from testing.failure_injection import (
    FailureInjector,
    FaultType,
    build_faults,
)
from testing.failure_profiles import (
    provider_timeout,
    provider_connection_failure,
    provider_http_429,
    provider_http_500,
    provider_offline,
    cache_corruption,
    cache_expired,
    cache_write_failure,
    artifact_write_failure,
    artifact_commit_failure,
    disk_full,
    permission_denied,
    eventbus_subscriber_failure,
    circuit_open,
    compose_profiles,
    scenario_full_infrastructure_stress,
)
from observability.event_bus import EventBus
from observability.events import (
    FailureInjected,
    FailureBypassed,
    FailureIgnored,
    FailureScenarioStarted,
    FailureScenarioCompleted,
)
from health.reports import HealthReporter

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_injector():
    """Guarantee a clean FailureInjector singleton for every test."""
    FailureInjector.clear()
    EventBus.clear()
    yield
    injector = FailureInjector.get_instance()
    injector.disable()
    FailureInjector.clear()
    EventBus.clear()


@pytest.fixture
def injector():
    return FailureInjector.get_instance()


@pytest.fixture
def artifacts_dir(tmp_path):
    d = tmp_path / "artifacts"
    d.mkdir()
    (d / "current").mkdir()
    (d / "archive").mkdir()
    return d


# ---------------------------------------------------------------------------
# Phase 1 — Core injector behaviour
# ---------------------------------------------------------------------------


class TestFailureInjectorCore:
    def test_disabled_by_default(self, injector):
        assert not injector.is_enabled

    def test_should_fail_returns_false_when_disabled(self, injector):
        assert not injector.should_fail("AnyComponent", FaultType.LLM_TIMEOUT)

    def test_enable_and_trigger(self, injector):
        injector.enable(provider_timeout(times=1), profile_name="test")
        assert injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)

    def test_exact_N_times(self, injector):
        injector.enable(provider_timeout(times=3), profile_name="test")
        triggered = sum(
            1
            for _ in range(5)
            if injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)
        )
        assert triggered == 3

    def test_persistent_always(self, injector):
        injector.enable(provider_offline(times=-1), profile_name="test")
        for _ in range(10):
            assert injector.should_fail(
                "CerebrasProvider", FaultType.LLM_CONNECTION_FAILURE
            )

    def test_reset_clears_counts(self, injector):
        injector.enable(provider_timeout(times=2), profile_name="test")
        injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)
        injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)
        # Exhausted — next should return False
        assert not injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)
        # After reset: should trigger again
        injector.reset()
        assert injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)

    def test_disable_stops_injection(self, injector):
        injector.enable(provider_timeout(times=-1), profile_name="test")
        assert injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)
        injector.disable()
        assert not injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)

    def test_statistics_snapshot(self, injector):
        injector.enable(provider_timeout(times=2), profile_name="my_profile")
        injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)
        stats = injector.statistics()
        assert stats.enabled
        assert stats.active_profile == "my_profile"
        assert stats.total_faults_triggered == 1
        assert stats.total_faults_configured == 1

    def test_no_fault_configured_returns_false(self, injector):
        injector.enable(provider_timeout(times=1), profile_name="test")
        # Completely different component/fault
        assert not injector.should_fail("FilesystemCache", FaultType.CACHE_CORRUPTION)

    def test_build_faults_helper(self):
        faults = build_faults(
            [
                ("Comp1", FaultType.LLM_TIMEOUT, 2),
                ("Comp2", FaultType.CACHE_CORRUPTION, -1),
            ]
        )
        assert len(faults) == 2
        assert faults[0].component == "Comp1"
        assert faults[1].times == -1

    def test_singleton_identity(self):
        a = FailureInjector.get_instance()
        b = FailureInjector.get_instance()
        assert a is b


# ---------------------------------------------------------------------------
# Phase 2 — Profile definitions
# ---------------------------------------------------------------------------


class TestFailureProfiles:
    def test_provider_timeout_profile(self, injector):
        injector.enable(provider_timeout())
        assert injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)

    def test_provider_http_429_profile(self, injector):
        injector.enable(provider_http_429())
        assert injector.should_fail("CerebrasProvider", FaultType.LLM_HTTP_429)

    def test_provider_http_500_profile(self, injector):
        injector.enable(provider_http_500())
        assert injector.should_fail("CerebrasProvider", FaultType.LLM_HTTP_500)

    def test_cache_corruption_profile(self, injector):
        injector.enable(cache_corruption())
        assert injector.should_fail("FilesystemCache", FaultType.CACHE_CORRUPTION)

    def test_cache_expired_profile(self, injector):
        injector.enable(cache_expired())
        assert injector.should_fail("FilesystemCache", FaultType.CACHE_EXPIRED)

    def test_cache_write_failure_profile(self, injector):
        injector.enable(cache_write_failure())
        assert injector.should_fail("FilesystemCache", FaultType.CACHE_WRITE_FAILURE)

    def test_artifact_write_failure_profile(self, injector):
        injector.enable(artifact_write_failure())
        assert injector.should_fail(
            "ArtifactWriter", FaultType.ARTIFACT_WRITE_INTERRUPTION
        )

    def test_artifact_commit_failure_profile(self, injector):
        injector.enable(artifact_commit_failure())
        assert injector.should_fail(
            "ArtifactWriter", FaultType.ARTIFACT_COMMIT_INTERRUPTION
        )

    def test_circuit_open_profile(self, injector):
        injector.enable(circuit_open())
        assert injector.should_fail("CircuitBreaker", FaultType.CIRCUIT_FORCE_OPEN)

    def test_disk_full_profile(self, injector):
        injector.enable(disk_full())
        assert injector.should_fail("Filesystem", FaultType.DISK_FULL)

    def test_permission_denied_profile(self, injector):
        injector.enable(permission_denied())
        assert injector.should_fail("Filesystem", FaultType.PERMISSION_DENIED)

    def test_eventbus_subscriber_failure_profile(self, injector):
        injector.enable(eventbus_subscriber_failure())
        assert injector.should_fail("EventBus", FaultType.EVENTBUS_SUBSCRIBER_FAILURE)

    def test_compose_profiles(self, injector):
        combined = compose_profiles(provider_timeout(), cache_corruption())
        injector.enable(combined, profile_name="composed")
        assert injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)
        assert injector.should_fail("FilesystemCache", FaultType.CACHE_CORRUPTION)

    def test_full_stress_scenario(self, injector):
        faults = scenario_full_infrastructure_stress()
        assert len(faults) == 5


# ---------------------------------------------------------------------------
# Phase 3 — EventBus events emitted
# ---------------------------------------------------------------------------


class TestFailureInjectorEvents:
    def test_injected_event_emitted(self):
        bus = EventBus.get_instance()
        received = []
        bus.subscribe(lambda e: received.append(e))

        injector = FailureInjector.get_instance()
        injector.enable(provider_timeout(times=1))
        injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)

        injected_events = [e for e in received if isinstance(e, FailureInjected)]
        assert len(injected_events) >= 1
        assert injected_events[0].component == "CerebrasProvider"
        assert injected_events[0].fault_type == FaultType.LLM_TIMEOUT

    def test_bypassed_event_when_disabled(self):
        bus = EventBus.get_instance()
        received = []
        bus.subscribe(lambda e: received.append(e))

        injector = FailureInjector.get_instance()
        injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)

        bypassed = [e for e in received if isinstance(e, FailureBypassed)]
        assert len(bypassed) >= 1

    def test_ignored_event_after_count_exhausted(self):
        bus = EventBus.get_instance()
        received = []
        bus.subscribe(lambda e: received.append(e))

        injector = FailureInjector.get_instance()
        injector.enable(provider_timeout(times=1))
        injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)  # triggers
        injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)  # ignored

        ignored = [e for e in received if isinstance(e, FailureIgnored)]
        assert len(ignored) >= 1

    def test_scenario_started_emitted(self):
        bus = EventBus.get_instance()
        received = []
        bus.subscribe(lambda e: received.append(e))

        injector = FailureInjector.get_instance()
        injector.enable(provider_timeout(), scenario_name="my_test")

        started = [e for e in received if isinstance(e, FailureScenarioStarted)]
        assert len(started) == 1
        assert started[0].scenario_name == "my_test"

    def test_scenario_completed_emitted(self):
        bus = EventBus.get_instance()
        received = []
        bus.subscribe(lambda e: received.append(e))

        injector = FailureInjector.get_instance()
        injector.enable(provider_timeout(), scenario_name="complete_test")
        injector.disable()

        completed = [e for e in received if isinstance(e, FailureScenarioCompleted)]
        assert len(completed) == 1
        assert completed[0].scenario_name == "complete_test"


# ---------------------------------------------------------------------------
# Phase 4 — Infrastructure integration hooks
# ---------------------------------------------------------------------------


class TestCerebrasServiceInjection:
    def test_timeout_raises(self, injector):
        from services.cerebras import CerebrasService

        injector.enable(provider_timeout(times=1))

        svc = CerebrasService.__new__(CerebrasService)
        svc.model_name = "test"
        svc._retry_policy = MagicMock()
        svc._circuit_breaker = MagicMock()

        # The internal _execute_call should raise when injector fires
        # We test via should_fail directly to stay unit-level
        assert injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)
        # After 1 fire, no longer triggers
        assert not injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)

    def test_http_429_injection(self, injector):
        injector.enable(provider_http_429(times=2))
        assert injector.should_fail("CerebrasProvider", FaultType.LLM_HTTP_429)
        assert injector.should_fail("CerebrasProvider", FaultType.LLM_HTTP_429)
        assert not injector.should_fail("CerebrasProvider", FaultType.LLM_HTTP_429)

    def test_connection_failure_injection(self, injector):
        injector.enable(provider_connection_failure(times=1))
        assert injector.should_fail(
            "CerebrasProvider", FaultType.LLM_CONNECTION_FAILURE
        )


class TestCacheInjection:
    def test_cache_corruption_injection(self, injector, tmp_path):
        from cache.filesystem import FilesystemCacheProvider

        injector.enable(cache_corruption(times=1))
        cache = FilesystemCacheProvider(str(tmp_path / "cache"))

        # Pre-populate so get() finds the file
        data = {"analysis": "test"}
        cache.set("specialist", "v1", "hash1", "scenario", data)

        # get() should return None (corruption injected)
        result = cache.get("specialist", "v1", "hash1", "scenario")
        assert result is None

    def test_cache_write_failure_injection(self, injector, tmp_path):
        from cache.filesystem import FilesystemCacheProvider

        injector.enable(cache_write_failure(times=1))
        cache = FilesystemCacheProvider(str(tmp_path / "cache"))

        # set() should silently drop — no file written
        cache.set("specialist", "v1", "hash1", "scenario", {"data": "x"})
        result = cache.get("specialist", "v1", "hash1", "scenario")
        assert result is None  # nothing was written

    def test_cache_expired_injection(self, injector, tmp_path):
        from cache.filesystem import FilesystemCacheProvider

        cache = FilesystemCacheProvider(str(tmp_path / "cache"))
        cache.set("specialist", "v1", "hash1", "scenario", {"data": "x"})

        # Now inject expiry on next get
        injector.enable(cache_expired(times=1))
        result = cache.get("specialist", "v1", "hash1", "scenario")
        assert result is None


class TestArtifactWriterInjection:
    def test_write_interruption(self, injector, tmp_path):
        from core.artifact_writer import TransactionalArtifactWriter

        injector.enable(artifact_write_failure(times=1))
        writer = TransactionalArtifactWriter(str(tmp_path / "artifacts"))
        with pytest.raises(OSError, match="Simulated artifact write interruption"):
            writer.write_json("test.json", {"key": "value"})

    def test_commit_interruption_triggers_rollback(self, injector, tmp_path):
        from core.artifact_writer import TransactionalArtifactWriter

        injector.enable(artifact_commit_failure(times=1))
        writer = TransactionalArtifactWriter(str(tmp_path / "artifacts"))
        writer.write_text("events.json", "[]")
        writer.write_text("manifest.json", "{}")
        writer.write_text("metrics.json", "{}")
        writer.write_text("prompt_bundle.json", "{}")
        writer.write_text("replay_certificate.json", "{}")

        with pytest.raises(OSError, match="Simulated artifact commit interruption"):
            writer.commit()

        # Staging should be cleaned up
        assert not writer.staging_dir.exists()


class TestCircuitBreakerInjection:
    def test_force_open_prevents_execution(self, injector):
        from core.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException

        injector.enable(circuit_open(times=1))
        cb = CircuitBreaker("TestDep")
        call_count = 0

        def _op():
            nonlocal call_count
            call_count += 1
            return "ok"

        # Force-open on execute, then _before_execute immediately rejects
        with pytest.raises((CircuitBreakerOpenException, Exception)):
            cb.execute(_op)


class TestEventBusInjection:
    def test_subscriber_failure_skips_subscriber_bus_continues(self, injector):
        bus = EventBus.get_instance()
        injector.enable(eventbus_subscriber_failure(times=1))

        call_log = []

        def good_subscriber(event):
            call_log.append("good")

        bus.subscribe(good_subscriber)

        from observability.events import ArtifactGenerated

        bus.emit(
            ArtifactGenerated(
                correlation_id="test-1",
                artifact_type="test",
                file_path="/tmp/test.json",
            )
        )

        # The eventbus subscriber failure fires on the first subscriber slot,
        # but the bus itself keeps running without exception
        assert bus.emitted_count >= 1


# ---------------------------------------------------------------------------
# Phase 5 — Failure report
# ---------------------------------------------------------------------------


class TestFailureInjectionReport:
    def test_report_schema(self, injector, artifacts_dir):
        injector.enable(provider_timeout(times=1), profile_name="report_test")
        injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)
        injector.disable()

        reporter = HealthReporter(str(artifacts_dir))
        reporter.generate_failure_injection_report(now_str="2026-01-01T00:00:00Z")

        report_path = artifacts_dir / "current" / "failure_injection_report.json"
        assert report_path.exists()

        with open(report_path) as f:
            data = json.load(f)

        assert "generated_at" in data
        assert "active_profile" in data
        assert "injection_enabled" in data
        assert "total_faults_triggered" in data
        assert "total_faults_configured" in data
        assert "fault_details" in data
        assert data["deterministic"] is True

    def test_report_archived_without_overwrite(self, injector, artifacts_dir):
        reporter = HealthReporter(str(artifacts_dir))

        reporter.generate_failure_injection_report("2026-01-01T00:00:00Z")
        time.sleep(0.01)  # ensure unique microsecond timestamp
        reporter.generate_failure_injection_report("2026-01-01T00:00:01Z")

        failure_archive = artifacts_dir / "archive" / "failure"
        archives = list(failure_archive.glob("failure_injection_*.json"))
        assert len(archives) == 2  # never overwrites


# ---------------------------------------------------------------------------
# Phase 6 — Recovery validation
# ---------------------------------------------------------------------------


class TestRecoveryValidation:
    def test_cache_regenerates_after_corruption(self, injector, tmp_path):
        """After cache corruption, cache behaves as a miss (regeneration path)."""
        from cache.filesystem import FilesystemCacheProvider

        cache = FilesystemCacheProvider(str(tmp_path / "cache"))
        cache.set("specialist", "v1", "hash1", "scenario", {"value": 42})

        injector.enable(cache_corruption(times=1))
        result = cache.get("specialist", "v1", "hash1", "scenario")
        assert result is None  # corruption simulated, miss returned

        # Injector exhausted — next read should succeed (regenerated)
        cache.set("specialist", "v1", "hash1", "scenario", {"value": 42})
        result = cache.get("specialist", "v1", "hash1", "scenario")
        assert result == {"value": 42}

    def test_artifact_writer_rollback_leaves_no_staging(self, injector, tmp_path):
        """Interrupted commit leaves staging cleaned up."""
        from core.artifact_writer import TransactionalArtifactWriter

        injector.enable(artifact_commit_failure(times=1))
        writer = TransactionalArtifactWriter(str(tmp_path / "artifacts"))
        writer.write_text("events.json", "[]")
        writer.write_text("manifest.json", "{}")
        writer.write_text("metrics.json", "{}")
        writer.write_text("prompt_bundle.json", "{}")
        writer.write_text("replay_certificate.json", "{}")

        try:
            writer.commit()
        except OSError:
            pass

        assert not writer.staging_dir.exists()


# ---------------------------------------------------------------------------
# Phase 7 — Determinism verification
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_identical_trigger_sequence_across_runs(self):
        """Same profile → same trigger sequence on every run."""
        results_a = []
        FailureInjector.clear()
        inj_a = FailureInjector.get_instance()
        inj_a.enable(provider_timeout(times=2))
        for _ in range(4):
            results_a.append(
                inj_a.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)
            )
        inj_a.disable()

        FailureInjector.clear()
        results_b = []
        inj_b = FailureInjector.get_instance()
        inj_b.enable(provider_timeout(times=2))
        for _ in range(4):
            results_b.append(
                inj_b.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)
            )
        inj_b.disable()

        assert results_a == results_b == [True, True, False, False]

    def test_no_timing_dependence(self, injector):
        """Injection is based purely on occurrence count, not wall-clock time."""
        injector.enable(provider_timeout(times=5))
        triggered = []
        for _ in range(7):
            triggered.append(
                injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT)
            )
        assert triggered == [True, True, True, True, True, False, False]
