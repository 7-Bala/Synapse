"""Deterministic Failure Injection Framework for Synapse infrastructure testing.

This module provides a singleton FailureInjector that can be configured to
deterministically simulate infrastructure faults during testing. It must NEVER
be referenced by reasoning logic, specialists, consensus, or orchestration.

Only infrastructure components (CerebrasService, FilesystemCacheProvider,
TransactionalArtifactWriter, RetryPolicy, CircuitBreaker, EventBus) may query it.
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from observability.event_bus import EventBus
from observability.events import (
    FailureBypassed,
    FailureInjected,
    FailureIgnored,
    FailureRecovered,
    FailureScenarioCompleted,
    FailureScenarioStarted,
)

# ---------------------------------------------------------------------------
# Fault type constants — infrastructure layer only
# ---------------------------------------------------------------------------


class FaultType:
    """Enumeration of supported deterministic fault types."""

    # LLM Provider
    LLM_TIMEOUT = "llm_timeout"
    LLM_CONNECTION_FAILURE = "llm_connection_failure"
    LLM_HTTP_429 = "llm_http_429"
    LLM_HTTP_500 = "llm_http_500"

    # Cache
    CACHE_CORRUPTION = "cache_corruption"
    CACHE_CHECKSUM_FAILURE = "cache_checksum_failure"
    CACHE_EXPIRED = "cache_expired"
    CACHE_WRITE_FAILURE = "cache_write_failure"
    CACHE_READ_FAILURE = "cache_read_failure"

    # Artifact Writer
    ARTIFACT_WRITE_INTERRUPTION = "artifact_write_interruption"
    ARTIFACT_COMMIT_INTERRUPTION = "artifact_commit_interruption"

    # Recovery
    RECOVERY_FAILURE = "recovery_failure"

    # Circuit Breaker
    CIRCUIT_FORCE_OPEN = "circuit_force_open"
    CIRCUIT_FORCE_HALF_OPEN = "circuit_force_half_open"

    # Retry
    RETRY_EXHAUSTION = "retry_exhaustion"

    # EventBus
    EVENTBUS_SUBSCRIBER_FAILURE = "eventbus_subscriber_failure"

    # Filesystem
    DISK_FULL = "disk_full"
    PERMISSION_DENIED = "permission_denied"

    # Prompt
    MISSING_PROMPT = "missing_prompt"
    INVALID_PROMPT_SCHEMA = "invalid_prompt_schema"

    # Replay / Artifact integrity
    INVALID_ARTIFACT = "invalid_artifact"
    INVALID_MANIFEST = "invalid_manifest"
    REPLAY_CORRUPTION = "replay_corruption"


@dataclass
class FaultConfig:
    """Configuration for a single deterministic fault target.

    Args:
        component: Infrastructure component name (e.g. "CerebrasProvider").
        fault_type: One of the FaultType constants.
        times: How many times this fault fires before becoming a no-op.
                Use -1 for persistent (always fires until reset).
        exception: Optional exception to raise when triggered. If None a
                   default exception is raised by the injector caller.
    """

    component: str
    fault_type: str
    times: int = 1  # -1 means always
    exception: Optional[Exception] = None

    # Internal tracking — not part of the profile definition
    _occurrence_count: int = field(default=0, init=False, repr=False, compare=False)

    def should_trigger(self) -> bool:
        """Returns True if this fault should fire on the next call."""
        if self.times == -1:
            return True  # persistent
        return self._occurrence_count < self.times

    def record_trigger(self) -> int:
        """Increments occurrence counter and returns the current occurrence number."""
        self._occurrence_count += 1
        return self._occurrence_count

    def reset(self) -> None:
        self._occurrence_count = 0


@dataclass
class InjectorStatistics:
    """Snapshot of injector activity."""

    enabled: bool
    active_profile: str
    total_faults_configured: int
    total_faults_triggered: int
    total_recoveries: int
    fault_details: List[Dict[str, Any]]


class FailureInjector:
    """Thread-safe singleton for deterministic failure injection.

    Usage (infrastructure code only):
        injector = FailureInjector.get_instance()
        if injector.should_fail("CerebrasProvider", FaultType.LLM_TIMEOUT):
            raise TimeoutError("Injected LLM timeout")
    """

    _instance: Optional["FailureInjector"] = None
    _lock: threading.Lock = threading.Lock()

    # Instance-level lock for thread-safe state mutation
    _state_lock: threading.RLock

    def __init__(self) -> None:
        self._state_lock = threading.RLock()
        self._enabled: bool = False
        self._active_profile: str = ""
        self._faults: List[FaultConfig] = []
        self._triggered_count: int = 0
        self._recovery_count: int = 0
        self._scenario_start: float = 0.0
        self._scenario_name: str = ""
        self._event_bus: Optional[EventBus] = None

    # ------------------------------------------------------------------
    # Singleton
    # ------------------------------------------------------------------

    @classmethod
    def get_instance(cls) -> "FailureInjector":
        """Returns the global singleton FailureInjector."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def clear(cls) -> None:
        """Resets the singleton — for isolated test teardown only."""
        with cls._lock:
            cls._instance = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def enable(
        self,
        faults: List[FaultConfig],
        profile_name: str = "custom",
        scenario_name: str = "test_scenario",
    ) -> None:
        """Activates the injector with a list of deterministic fault configs."""
        with self._state_lock:
            self._faults = list(faults)
            self._enabled = True
            self._active_profile = profile_name
            self._scenario_name = scenario_name
            self._triggered_count = 0
            self._recovery_count = 0
            self._scenario_start = time.time()

        self._emit_scenario_started(scenario_name, profile_name, len(faults))

    def disable(self) -> None:
        """Deactivates injection. Infrastructure operates normally."""
        with self._state_lock:
            if not self._enabled:
                return
            duration_ms = (time.time() - self._scenario_start) * 1000
            scenario = self._scenario_name
            profile = self._active_profile
            injected = self._triggered_count
            recovered = self._recovery_count
            self._enabled = False

        self._emit_scenario_completed(
            scenario, profile, injected, recovered, duration_ms
        )

    def reset(self) -> None:
        """Resets all fault occurrence counters without disabling."""
        with self._state_lock:
            for fault in self._faults:
                fault.reset()
            self._triggered_count = 0
            self._recovery_count = 0

    def should_fail(self, component: str, fault_type: str) -> bool:
        """Checks if a fault should be injected for the given component/type.

        Returns True and records the occurrence when the fault is active.
        Emits the appropriate observability event regardless.
        Never raises. The calling infrastructure code is responsible for
        actually raising / simulating the failure.
        """
        with self._state_lock:
            if not self._enabled:
                self._emit_bypassed(component, fault_type)
                return False

            for fault in self._faults:
                if fault.component == component and fault.fault_type == fault_type:
                    if fault.should_trigger():
                        occurrence = fault.record_trigger()
                        self._triggered_count += 1
                        self._emit_injected(component, fault_type, occurrence)
                        return True
                    else:
                        self._emit_ignored(
                            component, fault_type, reason="occurrence_limit_reached"
                        )
                        return False

            # No matching config → bypass
            self._emit_bypassed(component, fault_type)
            return False

    def get_exception(self, component: str, fault_type: str) -> Optional[Exception]:
        """Returns the configured exception for this fault, if any."""
        with self._state_lock:
            for fault in self._faults:
                if fault.component == component and fault.fault_type == fault_type:
                    return fault.exception
        return None

    def record_success(self, component: str) -> None:
        """Records that a component recovered successfully after a failure."""
        with self._state_lock:
            self._recovery_count += 1
        bus = self._get_event_bus()
        if bus:
            bus.emit(
                FailureRecovered(
                    correlation_id=f"fi_recovered_{component}_{time.time()}",
                    specialist=None,
                    component=component,
                    fault_type="recovered",
                )
            )

    def record_failure(self, component: str, fault_type: str) -> None:
        """Explicitly records a failure observation (for metrics tracking)."""
        with self._state_lock:
            self._triggered_count += 1
        self._emit_injected(component, fault_type, self._triggered_count)

    def statistics(self) -> InjectorStatistics:
        """Returns a snapshot of current injector statistics."""
        with self._state_lock:
            details = [
                {
                    "component": f.component,
                    "fault_type": f.fault_type,
                    "configured_times": f.times,
                    "triggered": f._occurrence_count,
                    "persistent": f.times == -1,
                }
                for f in self._faults
            ]
            return InjectorStatistics(
                enabled=self._enabled,
                active_profile=self._active_profile,
                total_faults_configured=len(self._faults),
                total_faults_triggered=self._triggered_count,
                total_recoveries=self._recovery_count,
                fault_details=details,
            )

    @property
    def is_enabled(self) -> bool:
        with self._state_lock:
            return self._enabled

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_event_bus(self) -> Optional[EventBus]:
        """Lazy-loads the event bus to avoid import cycles."""
        if self._event_bus is None:
            try:
                self._event_bus = EventBus.get_instance()
            except Exception:
                pass
        return self._event_bus

    def _emit_injected(self, component: str, fault_type: str, occurrence: int) -> None:
        if component == "EventBus":
            return
        bus = self._get_event_bus()
        if bus:
            try:
                bus.emit(
                    FailureInjected(
                        correlation_id=f"fi_{component}_{fault_type}_{occurrence}",
                        specialist=None,
                        component=component,
                        fault_type=fault_type,
                        occurrence=occurrence,
                    )
                )
            except Exception:
                pass

    def _emit_bypassed(self, component: str, fault_type: str) -> None:
        if component == "EventBus":
            return
        bus = self._get_event_bus()
        if bus:
            try:
                bus.emit(
                    FailureBypassed(
                        correlation_id=f"fi_bypassed_{component}_{fault_type}",
                        specialist=None,
                        component=component,
                        fault_type=fault_type,
                    )
                )
            except Exception:
                pass

    def _emit_ignored(self, component: str, fault_type: str, reason: str) -> None:
        if component == "EventBus":
            return
        bus = self._get_event_bus()
        if bus:
            try:
                bus.emit(
                    FailureIgnored(
                        correlation_id=f"fi_ignored_{component}_{fault_type}",
                        specialist=None,
                        component=component,
                        fault_type=fault_type,
                        reason=reason,
                    )
                )
            except Exception:
                pass

    def _emit_scenario_started(
        self, scenario: str, profile: str, fault_count: int
    ) -> None:
        bus = self._get_event_bus()
        if bus:
            try:
                bus.emit(
                    FailureScenarioStarted(
                        correlation_id=f"fi_scenario_started_{scenario}",
                        specialist=None,
                        scenario_name=scenario,
                        profile_name=profile,
                        fault_count=fault_count,
                    )
                )
            except Exception:
                pass

    def _emit_scenario_completed(
        self,
        scenario: str,
        profile: str,
        injected: int,
        recovered: int,
        duration_ms: float,
    ) -> None:
        bus = self._get_event_bus()
        if bus:
            try:
                bus.emit(
                    FailureScenarioCompleted(
                        correlation_id=f"fi_scenario_completed_{scenario}",
                        specialist=None,
                        scenario_name=scenario,
                        profile_name=profile,
                        injected_count=injected,
                        recovered_count=recovered,
                        duration_ms=duration_ms,
                    )
                )
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Convenience: build a list of FaultConfigs from a simple dict spec
# ---------------------------------------------------------------------------


def build_faults(spec: List[Tuple[str, str, int]]) -> List[FaultConfig]:
    """Build FaultConfig list from (component, fault_type, times) tuples."""
    return [FaultConfig(component=c, fault_type=f, times=t) for c, f, t in spec]
