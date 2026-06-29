"""Unit tests for the Circuit Breaker pattern."""

import time
import httpx
import threading
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from observability.event_bus import EventBus
from core.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException
from core.retry_policy import RetryPolicy


class MockEventBus(EventBus):
    def __init__(self):
        super().__init__()
        self.events = []

    def emit(self, event):
        self.events.append(event)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


def test_initial_closed_state():
    bus = MockEventBus()
    EventBus._instance = bus
    cb = CircuitBreaker("TestDep1")

    assert cb.state == "CLOSED"
    assert cb.failure_count == 0
    assert cb.success_count == 0
    assert cb.blocked_requests == 0

    def op():
        return "success"

    result = cb.execute(op)
    assert result == "success"
    assert cb.success_count == 1
    assert cb.state == "CLOSED"


def test_open_transition_and_blocked_requests():
    bus = MockEventBus()
    EventBus._instance = bus
    cb = CircuitBreaker("TestDep2")
    cb.failure_threshold = 3

    def op():
        raise httpx.TimeoutException("timeout")

    for _ in range(3):
        try:
            cb.execute(op)
        except httpx.TimeoutException:
            pass

    assert cb.state == "OPEN"
    assert cb.failure_count == 3

    # Next request should be blocked
    try:
        cb.execute(op)
        assert False, "Should have been blocked"
    except CircuitBreakerOpenException:
        pass

    assert cb.blocked_requests == 1

    events = [type(e).__name__ for e in bus.events]
    assert "CircuitOpened" in events
    assert "CircuitRejected" in events


def test_half_open_transition_and_successful_recovery():
    bus = MockEventBus()
    EventBus._instance = bus
    cb = CircuitBreaker("TestDep3")
    cb.failure_threshold = 2
    cb.recovery_timeout = 0.1
    cb.half_open_success_threshold = 2

    def fail_op():
        raise httpx.TimeoutException("timeout")

    def success_op():
        return "success"

    for _ in range(2):
        try:
            cb.execute(fail_op)
        except httpx.TimeoutException:
            pass

    assert cb.state == "OPEN"

    time.sleep(0.15)  # Wait for recovery timeout

    # First success
    result = cb.execute(success_op)
    assert result == "success"
    assert cb.state == "HALF_OPEN"

    # Second success (threshold reached)
    result = cb.execute(success_op)
    assert result == "success"
    assert cb.state == "CLOSED"

    events = [type(e).__name__ for e in bus.events]
    assert "CircuitHalfOpen" in events
    assert "CircuitClosed" in events
    assert "CircuitRecovered" in events


def test_half_open_failed_recovery():
    bus = MockEventBus()
    EventBus._instance = bus
    cb = CircuitBreaker("TestDep4")
    cb.failure_threshold = 2
    cb.recovery_timeout = 0.1
    cb.half_open_success_threshold = 2

    def fail_op():
        raise httpx.TimeoutException("timeout")

    def success_op():
        return "success"

    for _ in range(2):
        try:
            cb.execute(fail_op)
        except httpx.TimeoutException:
            pass

    assert cb.state == "OPEN"

    time.sleep(0.15)

    # First success
    cb.execute(success_op)
    assert cb.state == "HALF_OPEN"

    # Next failure trips it back to open immediately
    try:
        cb.execute(fail_op)
    except httpx.TimeoutException:
        pass

    assert cb.state == "OPEN"
    assert cb.opened_at > 0


def test_sliding_window_expiration():
    bus = MockEventBus()
    EventBus._instance = bus
    cb = CircuitBreaker("TestDep5")
    cb.failure_threshold = 2
    cb.sliding_window = 0.1

    def fail_op():
        raise httpx.TimeoutException("timeout")

    try:
        cb.execute(fail_op)
    except httpx.TimeoutException:
        pass

    assert cb.state == "CLOSED"

    time.sleep(0.15)  # First failure expires

    try:
        cb.execute(fail_op)
    except httpx.TimeoutException:
        pass

    assert cb.state == "CLOSED"
    assert len(cb._failure_timestamps) == 1


def test_thread_safety():
    bus = MockEventBus()
    EventBus._instance = bus
    cb = CircuitBreaker("TestDep6")

    def success_op():
        time.sleep(0.01)
        return "success"

    threads = []
    for _ in range(10):
        t = threading.Thread(target=cb.execute, args=(success_op,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    assert cb.success_count == 10
    assert cb.state == "CLOSED"


def test_retry_policy_integration():
    bus = MockEventBus()
    EventBus._instance = bus

    cb = CircuitBreaker("TestDep7")
    cb.failure_threshold = 1

    policy = RetryPolicy(bus)
    policy.max_attempts = 3
    policy.base_delay = 0.01

    def fail_op():
        raise httpx.TimeoutException("timeout")

    # Open the breaker
    try:
        cb.execute(fail_op)
    except httpx.TimeoutException:
        pass

    assert cb.state == "OPEN"

    # Now retry policy should execute and immediately fail
    try:
        policy.execute("req1", cb.execute, fail_op)
        assert False, "Should raise CircuitBreakerOpenException"
    except CircuitBreakerOpenException:
        pass

    # We should see retry_started and retry_failed_terminal, but no retry_attempt
    events = [type(e).__name__ for e in bus.events]
    assert "RetryStarted" in events
    assert "RetryFailedTerminal" in events
    assert "RetryAttempt" not in events


if __name__ == "__main__":
    test_initial_closed_state()
    test_open_transition_and_blocked_requests()
    test_half_open_transition_and_successful_recovery()
    test_half_open_failed_recovery()
    test_sliding_window_expiration()
    test_thread_safety()
    test_retry_policy_integration()
    print("All Circuit Breaker tests passed!")
