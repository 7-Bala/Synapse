"""Retry policy for infrastructure operations."""

import time
import random
from typing import Type, Tuple, Callable, Any
import httpx

from config.settings import settings
from observability.event_bus import EventBus
from observability.events import (
    RetryStarted,
    RetryAttempt,
    RetrySucceeded,
    RetryFailedTerminal,
    RetryExhausted
)

class RetryTimeoutException(Exception):
    """Raised when an operation exceeds its configured timeout."""
    pass


class RetryPolicy:
    """Production-grade retry framework for infrastructure operations."""

    # Default exception types that represent infrastructure/transient failures
    RETRYABLE_EXCEPTIONS: Tuple[Type[Exception], ...] = (
        RetryTimeoutException,
        httpx.TimeoutException,
        httpx.NetworkError,
        httpx.HTTPStatusError,
    )

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.max_attempts = settings.llm_max_retries
        self.base_delay = settings.retry_base_delay_ms / 1000.0
        self.max_delay = settings.retry_max_delay_ms / 1000.0
        self.jitter_enabled = settings.retry_jitter_enabled
        self.timeout = settings.llm_timeout_seconds

    def is_retryable(self, exception: Exception) -> bool:
        """Determines if the exception represents a transient infrastructure failure."""
        if isinstance(exception, httpx.HTTPStatusError):
            # Retry on 429 Too Many Requests and 5xx Server Errors
            status = exception.response.status_code
            if status in (429, 500, 502, 503, 504):
                return True
            return False

        for exc_type in self.RETRYABLE_EXCEPTIONS:
            if isinstance(exception, exc_type):
                return True
        return False

    def calculate_delay(self, attempt: int) -> float:
        """Calculates exponential backoff with optional jitter."""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        if self.jitter_enabled:
            delay += random.uniform(0, 0.1 * delay)  # 10% jitter
        return delay

    def _emit_event(self, event_type: str, request_id: str, attempt: int, **kwargs: Any) -> None:
        """Emits telemetry to the EventBus."""
        base_kwargs = {
            "correlation_id": request_id,
            "attempt": attempt,
            "specialist": "Infrastructure"
        }
        base_kwargs.update(kwargs)

        if event_type == "retry_started":
            event = RetryStarted(**base_kwargs)
        elif event_type == "retry_attempt":
            event = RetryAttempt(**base_kwargs)
        elif event_type == "retry_succeeded":
            event = RetrySucceeded(**base_kwargs)
        elif event_type == "retry_failed_terminal":
            event = RetryFailedTerminal(**base_kwargs)
        elif event_type == "retry_exhausted":
            event = RetryExhausted(**base_kwargs)
        else:
            raise ValueError(f"Unknown retry event type: {event_type}")

        self.event_bus.publish(event)

    def execute(self, request_id: str, operation: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Executes the operation with retry and telemetry logic."""
        attempt = 0
        self._emit_event("retry_started", request_id, attempt)

        while True:
            attempt_start = time.time()
            try:
                # The operation itself is expected to respect self.timeout if applicable.
                result = operation(*args, **kwargs)

                duration_ms = (time.time() - attempt_start) * 1000
                if attempt > 0:
                    self._emit_event("retry_succeeded", request_id, attempt, duration_ms=duration_ms)

                return result

            except httpx.TimeoutException:
                exc = RetryTimeoutException("Operation timed out")
                duration_ms = (time.time() - attempt_start) * 1000
                if not self._handle_failure(request_id, attempt, exc, duration_ms):
                    raise exc

            except Exception as e:
                duration_ms = (time.time() - attempt_start) * 1000
                if not self._handle_failure(request_id, attempt, e, duration_ms):
                    raise e

            delay = self.calculate_delay(attempt)
            time.sleep(delay)
            attempt += 1

    def _handle_failure(self, request_id: str, attempt: int, exception: Exception, duration_ms: float) -> bool:
        """Evaluates whether to retry or raise the exception. Returns True if we should retry, False to raise."""
        if not self.is_retryable(exception):
            self._emit_event("retry_failed_terminal", request_id, attempt, duration_ms=duration_ms, error=str(exception))
            return False

        if attempt >= self.max_attempts:
            self._emit_event("retry_exhausted", request_id, attempt, duration_ms=duration_ms, error=str(exception))
            return False

        delay = self.calculate_delay(attempt)
        self._emit_event("retry_attempt", request_id, attempt, duration_ms=duration_ms, error=str(exception), delay_ms=delay * 1000)
        return True
