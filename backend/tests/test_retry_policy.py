"""Unit tests for RetryPolicy."""

import httpx
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.retry_policy import RetryPolicy, RetryTimeoutException


class MockEventBus:
    def __init__(self):
        self.events = []

    def publish(self, event):
        self.events.append(event)

    def emit(self, event):
        self.events.append(event)


def test_success_without_retry():
    bus = MockEventBus()
    policy = RetryPolicy(bus)
    policy.max_attempts = 3

    def op():
        return "success"

    result = policy.execute("req1", op)

    assert result == "success"
    assert len(bus.events) == 1
    assert type(bus.events[0]).__name__ == "RetryStarted"


def test_success_after_retry():
    bus = MockEventBus()
    policy = RetryPolicy(bus)
    policy.max_attempts = 3
    policy.base_delay = 0.0  # speed up test
    policy.max_delay = 0.0

    attempts = 0
    def op():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise httpx.TimeoutException("timeout")
        return "success"

    result = policy.execute("req2", op)

    assert result == "success"
    assert attempts == 2

    types = [type(e).__name__ for e in bus.events]
    assert "RetryStarted" in types
    assert "RetryAttempt" in types
    assert "RetrySucceeded" in types


def test_retry_exhaustion():
    bus = MockEventBus()
    policy = RetryPolicy(bus)
    policy.max_attempts = 3
    policy.base_delay = 0.0
    policy.max_delay = 0.0

    def op():
        raise httpx.TimeoutException("timeout")

    try:
        policy.execute("req3", op)
        assert False, "Should have raised exception"
    except RetryTimeoutException:
        pass

    types = [type(e).__name__ for e in bus.events]
    assert "RetryStarted" in types
    assert "RetryAttempt" in types
    assert "RetryExhausted" in types


def test_non_retryable_exception():
    bus = MockEventBus()
    policy = RetryPolicy(bus)
    policy.max_attempts = 3

    def op():
        raise ValueError("Invalid configuration")

    try:
        policy.execute("req4", op)
        assert False, "Should have raised exception"
    except ValueError:
        pass

    types = [type(e).__name__ for e in bus.events]
    assert "RetryStarted" in types
    assert "RetryFailedTerminal" in types
    assert "RetryAttempt" not in types


def test_exponential_backoff_calculation():
    bus = MockEventBus()
    policy = RetryPolicy(bus)
    policy.base_delay = 1.0
    policy.max_delay = 5.0
    policy.jitter_enabled = False

    assert policy.calculate_delay(0) == 1.0
    assert policy.calculate_delay(1) == 2.0
    assert policy.calculate_delay(2) == 4.0
    assert policy.calculate_delay(3) == 5.0  # maxes out

if __name__ == "__main__":
    test_success_without_retry()
    test_success_after_retry()
    test_retry_exhaustion()
    test_non_retryable_exception()
    test_exponential_backoff_calculation()
    print("All RetryPolicy tests passed!")
