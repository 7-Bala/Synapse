"""Metrics logging utility."""

from dataclasses import dataclass


@dataclass
class SpecialistMetrics:
    """Metrics for a single specialist execution."""

    specialist: str
    started_at: str
    finished_at: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cache_hit: bool
    status: str


class MetricsLogger:
    """Logs execution metrics."""

    @staticmethod
    def log(metrics: SpecialistMetrics) -> None:
        """Logs metrics (typically to the pipeline state or a file in a real impl).

        For this framework, we can just print or collect them,
        since PipelineState manages the global list.
        """
        pass
