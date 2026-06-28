"""Latency tracking utility."""

import time
from typing import Dict


class LatencyTracker:
    """Tracks latency for synchronous and asynchronous operations."""

    def __init__(self):
        self._start_times: Dict[str, float] = {}

    def start(self, operation_id: str) -> None:
        """Starts a timer for a specific operation."""
        self._start_times[operation_id] = time.time()

    def stop(self, operation_id: str) -> int:
        """Stops the timer and returns elapsed time in milliseconds."""
        if operation_id not in self._start_times:
            return 0

        start_time = self._start_times.pop(operation_id)
        elapsed_seconds = time.time() - start_time
        return int(elapsed_seconds * 1000)
