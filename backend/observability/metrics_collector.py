"""Observability metrics collector for the Synapse backend."""

import json
import os
from typing import Dict, List, Any

from .events import (
    BaseEvent,
    SpecialistStarted,
    SpecialistFinished,
    LLMRequestStarted,
    LLMRequestFinished,
    CacheLookupStarted,
    CacheLookupFinished,
    CacheHit,
    CacheMiss,
    ValidationStarted,
    ValidationFinished,
)
from .event_bus import EventBus


class MetricsCollector:
    """Subscribes to EventBus and derives latencies passively."""

    def __init__(self, output_dir: str, event_bus: EventBus):
        self.output_dir = output_dir
        self.event_bus = event_bus
        self.event_bus.subscribe(self.handle_event)

        os.makedirs(output_dir, exist_ok=True)

        # State tracking for ongoing traces
        self._traces: Dict[str, Dict[str, Any]] = {}
        # Final aggregated metrics
        self.metrics: Dict[str, List[Dict[str, Any]]] = {}

    def _get_trace(self, correlation_id: str, specialist: str) -> Dict[str, Any]:
        """Gets or creates a trace record for a specific tick and specialist."""
        key = f"{correlation_id}:{specialist}"
        if key not in self._traces:
            self._traces[key] = {
                "specialist": specialist,
                "correlation_id": correlation_id,
                "execution_start": 0.0,
                "execution_finish": 0.0,
                "llm_start": 0.0,
                "cache_start": 0.0,
                "validation_start": 0.0,
                "total_latency_ms": 0,
                "llm_latency_ms": 0,
                "cache_lookup_time_ms": 0,
                "validation_latency_ms": 0,
                "tokens_in": 0,
                "tokens_out": 0,
                "cache_hit": False,
                "execution_status": "UNKNOWN",
                "confidence_produced": 0.0,
            }
        return self._traces[key]

    def _handle_specialist_started(
        self, trace: Dict[str, Any], event: SpecialistStarted
    ) -> None:
        trace["execution_start"] = event.timestamp

    def _handle_llm_request_started(
        self, trace: Dict[str, Any], event: LLMRequestStarted
    ) -> None:
        trace["llm_start"] = event.timestamp

    def _handle_llm_request_finished(
        self, trace: Dict[str, Any], event: LLMRequestFinished
    ) -> None:
        latency = event.timestamp - trace.get("llm_start", event.timestamp)
        trace["llm_latency_ms"] = int(latency * 1000)
        trace["tokens_in"] = event.tokens_in
        trace["tokens_out"] = event.tokens_out

    def _handle_cache_lookup_started(
        self, trace: Dict[str, Any], event: CacheLookupStarted
    ) -> None:
        trace["cache_start"] = event.timestamp

    def _handle_cache_lookup_finished(
        self, trace: Dict[str, Any], event: CacheLookupFinished
    ) -> None:
        latency = event.timestamp - trace.get("cache_start", event.timestamp)
        trace["cache_lookup_time_ms"] = int(latency * 1000)

    def _handle_cache_hit(self, trace: Dict[str, Any], event: CacheHit) -> None:
        trace["cache_hit"] = True

    def _handle_cache_miss(self, trace: Dict[str, Any], event: CacheMiss) -> None:
        trace["cache_hit"] = False

    def _handle_validation_started(
        self, trace: Dict[str, Any], event: ValidationStarted
    ) -> None:
        trace["validation_start"] = event.timestamp

    def _handle_validation_finished(
        self, trace: Dict[str, Any], event: ValidationFinished
    ) -> None:
        latency = event.timestamp - trace.get("validation_start", event.timestamp)
        trace["validation_latency_ms"] = int(latency * 1000)

    def _handle_specialist_finished(
        self, trace: Dict[str, Any], event: SpecialistFinished
    ) -> None:
        trace["execution_finish"] = event.timestamp
        latency = event.timestamp - trace.get("execution_start", event.timestamp)
        trace["total_latency_ms"] = int(latency * 1000)
        trace["execution_status"] = event.status
        trace["confidence_produced"] = event.confidence
        self.metrics.setdefault(event.correlation_id, []).append(trace)

    def handle_event(self, event: BaseEvent) -> None:  # noqa: C901
        """Process an event out-of-band to compute metrics."""
        specialist = getattr(event, "specialist", None)
        if not specialist:
            return

        trace = self._get_trace(event.correlation_id, specialist)

        if isinstance(event, SpecialistStarted):
            self._handle_specialist_started(trace, event)
        elif isinstance(event, LLMRequestStarted):
            self._handle_llm_request_started(trace, event)
        elif isinstance(event, LLMRequestFinished):
            self._handle_llm_request_finished(trace, event)
        elif isinstance(event, CacheLookupStarted):
            self._handle_cache_lookup_started(trace, event)
        elif isinstance(event, CacheLookupFinished):
            self._handle_cache_lookup_finished(trace, event)
        elif isinstance(event, CacheHit):
            self._handle_cache_hit(trace, event)
        elif isinstance(event, CacheMiss):
            self._handle_cache_miss(trace, event)
        elif isinstance(event, ValidationStarted):
            self._handle_validation_started(trace, event)
        elif isinstance(event, ValidationFinished):
            self._handle_validation_finished(trace, event)
        elif isinstance(event, SpecialistFinished):
            self._handle_specialist_finished(trace, event)

    def export(self, version_prefix: str = "metrics_report") -> str:
        """Exports the aggregated metrics to a JSON report."""
        version = 1
        while os.path.exists(
            os.path.join(self.output_dir, f"{version_prefix}_v{version}.json")
        ):
            version += 1

        file_path = os.path.join(self.output_dir, f"{version_prefix}_v{version}.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.metrics, f, indent=2)

        return file_path
