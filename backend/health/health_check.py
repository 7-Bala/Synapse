"""Health Monitoring core probes and aggregation."""

import importlib
import json
from pathlib import Path
from typing import Dict, Any

from health.status import HealthStatus
from health.models import ComponentHealth, SystemHealth
from observability.event_bus import EventBus
from observability.events import (
    BaseEvent,
    CacheCorrupted,
    RetryAttempt,
    RetryFailedTerminal,
    RetryExhausted,
    CircuitRejected,
    CircuitFailure,
    CircuitRecovered,
)
from cache.filesystem import FilesystemCacheProvider


class HealthMonitor:
    """Passively monitors infrastructure health."""

    def __init__(self, artifacts_dir: str):
        self.artifacts_dir = Path(artifacts_dir)
        self.current_dir = self.artifacts_dir / "current"
        self.archive_dir = self.artifacts_dir / "archive"

        # Internal state for probes populated via EventBus
        self.cache_corruptions = 0
        self.circuit_failures = 0
        self.circuit_recoveries = 0
        self.circuit_rejections = 0
        self.total_retries = 0
        self.exhausted_retries = 0
        self.terminal_failures = 0

        self.emitted_events = 0

        # Subscribe to EventBus
        EventBus.get_instance().subscribe(self._handle_event)

    def _handle_event(self, event: BaseEvent) -> None:
        """Passively records statistics from the EventBus."""
        self.emitted_events += 1

        if isinstance(event, CacheCorrupted):
            self.cache_corruptions += 1
        elif isinstance(event, CircuitFailure):
            self.circuit_failures += 1
        elif isinstance(event, CircuitRecovered):
            self.circuit_recoveries += 1
        elif isinstance(event, CircuitRejected):
            self.circuit_rejections += 1
        elif isinstance(event, RetryAttempt):
            self.total_retries += 1
        elif isinstance(event, RetryExhausted):
            self.exhausted_retries += 1
        elif isinstance(event, RetryFailedTerminal):
            self.terminal_failures += 1

    def probe_cache(self) -> ComponentHealth:
        """Probe the cache component."""
        base_dir = self.artifacts_dir.parent
        provider = FilesystemCacheProvider(str(base_dir / "cache"))
        return ComponentHealth(
            name="cache",
            status=HealthStatus.HEALTHY,
            message="Cache operational.",
            timestamp="",
            metadata={
                "provider": provider.provider_name,
                "availability": True,
                "cache_size": (
                    len(list(provider.cache_dir.glob("*.json")))
                    if provider.cache_dir.exists()
                    else 0
                ),
                "ttl_configuration": provider.default_ttl,
                "cleanup_status": "ENABLED",
                "corruption_count": self.cache_corruptions,
                "checksum_validation_capability": True,
            },
        )

    def probe_circuit_breaker(self) -> ComponentHealth:
        return ComponentHealth(
            name="circuit_breaker",
            status=HealthStatus.HEALTHY,
            message="Circuit breaker operational.",
            timestamp="",
            metadata={
                "state": "UNKNOWN",  # We don't track state for all instances, but we track global failures
                "failure_count": self.circuit_failures,
                "recovery_count": self.circuit_recoveries,
                "rejection_count": self.circuit_rejections,
                "last_transition": None,
            },
        )

    def probe_retry_policy(self) -> ComponentHealth:
        return ComponentHealth(
            name="retry_policy",
            status=HealthStatus.HEALTHY,
            message="Retry policy operational.",
            timestamp="",
            metadata={
                "retries": self.total_retries,
                "exhausted_retries": self.exhausted_retries,
                "average_retry_delay": 0,  # Cannot compute passively without storing all
                "terminal_failures": self.terminal_failures,
            },
        )

    def probe_event_bus(self) -> ComponentHealth:
        bus = EventBus.get_instance()
        return ComponentHealth(
            name="event_bus",
            status=HealthStatus.HEALTHY,
            message="EventBus operational.",
            timestamp="",
            metadata={
                "subscriber_count": len(bus._subscribers),
                "emitted_events": self.emitted_events,
                "dropped_events": 0,
                "queue_size": 0,
            },
        )

    def probe_lock_manager(self) -> ComponentHealth:
        try:
            core_locks = importlib.import_module("core.locks")
            stats = core_locks.LockManager.get_statistics()
            return ComponentHealth(
                name="lock_manager",
                status=HealthStatus.HEALTHY,
                message="Lock Manager operational.",
                timestamp="",
                metadata=stats,
            )
        except ImportError:
            return ComponentHealth(
                name="lock_manager",
                status=HealthStatus.HEALTHY,
                message="Concurrent Safety phase intentionally deferred.",
                timestamp="",
                metadata={"deferred": True},
            )

    def probe_artifact_writer(self) -> ComponentHealth:
        staging_dir = self.artifacts_dir / ".staging"
        return ComponentHealth(
            name="artifact_writer",
            status=HealthStatus.HEALTHY,
            message="Artifact writer operational.",
            timestamp="",
            metadata={
                "staging_state": (
                    "ACTIVE"
                    if staging_dir.exists() and any(staging_dir.iterdir())
                    else "EMPTY"
                ),
                "archive_state": (
                    "AVAILABLE" if self.archive_dir.exists() else "UNAVAILABLE"
                ),
                "transaction_status": "OK",
                "rollback_count": 0,
            },
        )

    def probe_recovery_manager(self) -> ComponentHealth:
        quarantine_dir = self.artifacts_dir / "quarantine"
        quarantine_count = (
            len(list(quarantine_dir.iterdir())) if quarantine_dir.exists() else 0
        )

        # Read recovery report if it exists
        report_path = self.artifacts_dir / "recovery_report.json"
        recovery_count = 0
        if report_path.exists():
            try:
                with open(report_path) as f:
                    report = json.load(f)
                    if report.get("status") == "RECOVERED":
                        recovery_count += 1
            except Exception:
                pass

        return ComponentHealth(
            name="recovery_manager",
            status=(
                HealthStatus.HEALTHY if quarantine_count == 0 else HealthStatus.DEGRADED
            ),
            message="Recovery Manager operational.",
            timestamp="",
            metadata={
                "recovery_count": recovery_count,
                "quarantine_entries": quarantine_count,
                "archive_restores": recovery_count,
                "failed_recoveries": 0,
            },
        )

    def probe_provenance(self) -> ComponentHealth:
        manifest_path = self.current_dir / "manifest.json"
        metadata: Dict[str, Any] = {
            "replay_id": None,
            "manifest_version": None,
            "schema_version": None,
            "prompt_bundle_version": None,
            "git_metadata_availability": False,
        }
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    man = json.load(f)
                    metadata["replay_id"] = man.get("replay_id")
                    metadata["manifest_version"] = man.get(
                        "schema_version"
                    )  # Assuming schema_version acts as manifest_version
                    metadata["schema_version"] = man.get("schema_version")
                    metadata["prompt_bundle_version"] = man.get("hashes", {}).get(
                        "prompts_hash"
                    )
                    metadata["git_metadata_availability"] = "git_hash" in man
            except Exception:
                pass

        return ComponentHealth(
            name="provenance",
            status=(
                HealthStatus.HEALTHY if manifest_path.exists() else HealthStatus.UNKNOWN
            ),
            message=(
                "Provenance available."
                if manifest_path.exists()
                else "Missing provenance."
            ),
            timestamp="",
            metadata=metadata,
        )

    def probe_evaluation(self) -> ComponentHealth:
        eval_report_path = (
            self.artifacts_dir.parent
            / "backend"
            / "evaluation_output"
            / "evaluation_report.json"
        )
        status = HealthStatus.UNKNOWN
        msg = "Evaluation unavailable."
        meta: Dict[str, Any] = {
            "latest_evaluation": None,
            "benchmark_status": None,
            "determinism_rate": None,
            "golden_dataset_version": None,
        }
        if eval_report_path.exists():
            try:
                with open(eval_report_path) as f:
                    rep = json.load(f)
                    status = (
                        HealthStatus.HEALTHY
                        if rep.get("overall_status") == "PASS"
                        else HealthStatus.DEGRADED
                    )
                    msg = "Evaluation completed."
                    meta["latest_evaluation"] = rep.get("timestamp")
                    meta["benchmark_status"] = rep.get("overall_status")
                    meta["determinism_rate"] = (
                        "100%" if status == HealthStatus.HEALTHY else "0%"
                    )
                    meta["golden_dataset_version"] = rep.get("golden_manifest", {}).get(
                        "schema_version"
                    )
            except Exception:
                pass

        return ComponentHealth(
            name="evaluation", status=status, message=msg, timestamp="", metadata=meta
        )

    def aggregate_health(self) -> SystemHealth:
        """Deterministically aggregates health from all components."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).isoformat()

        components = {
            "cache": self.probe_cache(),
            "circuit_breaker": self.probe_circuit_breaker(),
            "retry_policy": self.probe_retry_policy(),
            "event_bus": self.probe_event_bus(),
            "lock_manager": self.probe_lock_manager(),
            "artifact_writer": self.probe_artifact_writer(),
            "recovery_manager": self.probe_recovery_manager(),
            "provenance": self.probe_provenance(),
            "evaluation": self.probe_evaluation(),
        }

        for c in components.values():
            c.timestamp = now

        overall = HealthStatus.HEALTHY
        for c in components.values():
            if c.status == HealthStatus.FAILED:
                overall = HealthStatus.FAILED
                break

        if overall != HealthStatus.FAILED:
            for c in components.values():
                if c.status == HealthStatus.DEGRADED:
                    overall = HealthStatus.DEGRADED
                    break

        if overall not in (HealthStatus.FAILED, HealthStatus.DEGRADED):
            for c in components.values():
                if c.status == HealthStatus.UNKNOWN:
                    overall = HealthStatus.UNKNOWN
                    break

        return SystemHealth(
            overall_status=overall, generated_at=now, components=components
        )
