"""Enterprise Circuit Breaker for infrastructure protection."""

import time
import threading
from enum import Enum
from typing import Any, Callable, List
import httpx

from config.settings import settings
from observability.event_bus import EventBus
from observability.events import (
    CircuitOpened,
    CircuitClosed,
    CircuitHalfOpen,
    CircuitRejected,
    CircuitFailure,
    CircuitRecovered,
)


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenException(Exception):
    """Raised when the circuit breaker rejects a request because it is OPEN."""

    pass


def is_breaker_failure(exception: Exception) -> bool:
    """
    Determines if the exception represents an infrastructure failure that
    should contribute to opening the circuit breaker.
    """
    if isinstance(exception, httpx.HTTPStatusError):
        status = exception.response.status_code
        if status in (429, 500, 502, 503, 504):
            return True
        return False

    if isinstance(
        exception,
        (httpx.TimeoutException, httpx.NetworkError, TimeoutError, ConnectionError),
    ):
        return True

    # Do not count internal logic exceptions, validations, or timeouts already handled
    return False


class CircuitBreaker:
    """
    Protects Synapse from cascading infrastructure failures.
    Maintains a sliding window of failures and transitions state deterministically.
    """

    def __init__(self, dependency_name: str):
        self.dependency_name = dependency_name
        self.event_bus = EventBus.get_instance()

        self.enabled = settings.circuit_breaker_enabled
        self.failure_threshold = settings.circuit_breaker_failure_threshold
        self.success_threshold = settings.circuit_breaker_success_threshold
        self.sliding_window = settings.circuit_breaker_sliding_window_seconds
        self.recovery_timeout = settings.circuit_breaker_recovery_timeout_seconds
        self.half_open_max = settings.circuit_breaker_half_open_max_requests
        self.half_open_success_threshold = (
            settings.circuit_breaker_half_open_success_threshold
        )

        self._state = CircuitState.CLOSED

        # State metrics
        self.failure_count = 0
        self.success_count = 0
        self.last_failure: float = 0.0
        self.last_success: float = 0.0
        self.opened_at: float = 0.0
        self.last_transition: float = time.time()

        self.blocked_requests = 0
        self.allowed_requests = 0
        self.recovery_attempts = 0

        self.consecutive_failures = 0
        self.consecutive_successes = 0

        # Half open state tracking
        self.half_open_requests = 0

        # Sliding window history
        self._failure_timestamps: List[float] = []

        # Thread safety
        self._lock = threading.RLock()

    @property
    def state(self) -> str:
        return self._state.value

    @property
    def next_retry(self) -> float:
        if self._state == CircuitState.OPEN:
            return self.opened_at + self.recovery_timeout
        return 0.0

    def _cleanup_sliding_window(self, current_time: float) -> None:
        """Removes expired failures from the sliding window."""
        cutoff = current_time - self.sliding_window
        self._failure_timestamps = [t for t in self._failure_timestamps if t >= cutoff]

    def _transition_to_open(self, reason: str, current_time: float) -> None:
        self._state = CircuitState.OPEN
        self.opened_at = current_time
        self.last_transition = current_time
        self.event_bus.emit(
            CircuitOpened(
                specialist=None,
                correlation_id=f"cb_{self.dependency_name}_{current_time}",
                dependency=self.dependency_name,
                reason=reason,
            )
        )

    def _transition_to_half_open(self, current_time: float) -> None:
        self._state = CircuitState.HALF_OPEN
        self.last_transition = current_time
        self.half_open_requests = 0
        self.consecutive_successes = 0
        self.recovery_attempts += 1
        self.event_bus.emit(
            CircuitHalfOpen(
                specialist=None,
                correlation_id=f"cb_{self.dependency_name}_{current_time}",
                dependency=self.dependency_name,
            )
        )

    def _transition_to_closed(self, current_time: float) -> None:
        self._state = CircuitState.CLOSED
        self.last_transition = current_time
        self.consecutive_failures = 0
        self._failure_timestamps.clear()
        self.event_bus.emit(
            CircuitClosed(
                specialist=None,
                correlation_id=f"cb_{self.dependency_name}_{current_time}",
                dependency=self.dependency_name,
            )
        )
        self.event_bus.emit(
            CircuitRecovered(
                specialist=None,
                correlation_id=f"cb_{self.dependency_name}_{current_time}",
                dependency=self.dependency_name,
            )
        )

    def _before_execute(self, current_time: float) -> None:
        """Evaluates state before allowing execution."""
        with self._lock:
            if not self.enabled:
                self.allowed_requests += 1
                return

            if self._state == CircuitState.OPEN:
                if current_time >= self.next_retry:
                    self._transition_to_half_open(current_time)
                else:
                    self.blocked_requests += 1
                    self.event_bus.emit(
                        CircuitRejected(
                            specialist=None,
                            correlation_id=f"cb_{self.dependency_name}_{current_time}",
                            dependency=self.dependency_name,
                        )
                    )
                    raise CircuitBreakerOpenException(
                        f"Circuit Breaker for {self.dependency_name} is OPEN."
                    )

            if self._state == CircuitState.HALF_OPEN:
                if self.half_open_requests >= self.half_open_max:
                    self.blocked_requests += 1
                    self.event_bus.emit(
                        CircuitRejected(
                            specialist=None,
                            correlation_id=f"cb_{self.dependency_name}_{current_time}",
                            dependency=self.dependency_name,
                        )
                    )
                    raise CircuitBreakerOpenException(
                        f"Circuit Breaker for {self.dependency_name} is HALF_OPEN and max requests reached."
                    )
                self.half_open_requests += 1

            self.allowed_requests += 1

    def _on_success(self, current_time: float) -> None:
        """Called upon successful execution."""
        with self._lock:
            if not self.enabled:
                return

            self.success_count += 1
            self.consecutive_successes += 1
            self.consecutive_failures = 0
            self.last_success = current_time

            if self._state == CircuitState.HALF_OPEN:
                if self.consecutive_successes >= self.half_open_success_threshold:
                    self._transition_to_closed(current_time)

            elif self._state == CircuitState.CLOSED:
                self._cleanup_sliding_window(current_time)

    def _on_failure(self, current_time: float, exception: Exception) -> None:
        """Called upon execution failure."""
        with self._lock:
            if not self.enabled:
                return

            # Only count infrastructure failures
            if not is_breaker_failure(exception):
                return

            self.failure_count += 1
            self.consecutive_failures += 1
            self.consecutive_successes = 0
            self.last_failure = current_time

            self.event_bus.emit(
                CircuitFailure(
                    specialist=None,
                    correlation_id=f"cb_{self.dependency_name}_{current_time}",
                    dependency=self.dependency_name,
                    error=str(exception),
                )
            )

            if self._state == CircuitState.HALF_OPEN:
                # Immediate trip back to open
                self._transition_to_open(
                    reason="Half-open request failed", current_time=current_time
                )

            elif self._state == CircuitState.CLOSED:
                self._cleanup_sliding_window(current_time)
                self._failure_timestamps.append(current_time)
                if len(self._failure_timestamps) >= self.failure_threshold:
                    self._transition_to_open(
                        reason="Failure threshold reached", current_time=current_time
                    )

    def execute(self, operation: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Executes the operation through the circuit breaker."""
        current_time = time.time()

        self._before_execute(current_time)

        try:
            result = operation(*args, **kwargs)
            self._on_success(time.time())
            return result
        except Exception as e:
            # We don't catch and swallow exceptions. We just observe them.
            self._on_failure(time.time(), e)
            raise e
