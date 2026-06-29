import json
import time
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock

import pytest

from cache.filesystem import FilesystemCacheProvider
from observability.event_bus import EventBus
from observability.events import (
    CacheCleanupFinished,
    CacheCorrupted,
    CacheExpired,
    CacheHit,
    CacheMiss,
    CacheWrite,
)


@pytest.fixture
def temp_cache_dir(tmp_path):
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return str(cache_dir)


@pytest.fixture
def event_bus():
    bus = EventBus(enabled=True)
    bus.clear()  # reset singleton just in case
    return bus


@pytest.fixture
def cache_provider(temp_cache_dir, event_bus):
    return FilesystemCacheProvider(temp_cache_dir, event_bus=event_bus)


def test_cache_miss(cache_provider, event_bus):
    subscriber = Mock()
    event_bus.subscribe(subscriber)

    result = cache_provider.get("SourceAgent", "1.0", "hash123", "scenario1")
    assert result is None

    # Verify CacheMiss event was emitted
    assert subscriber.call_count == 1
    event = subscriber.call_args[0][0]
    assert isinstance(event, CacheMiss)


def test_cache_write_and_hit(cache_provider, event_bus):
    subscriber = Mock()
    event_bus.subscribe(subscriber)

    payload = {"decision": "proceed", "confidence": 0.9}
    cache_provider.set("SourceAgent", "1.0", "hash123", "scenario1", payload)

    # Verify CacheWrite event
    write_event = [
        call[0][0]
        for call in subscriber.call_args_list
        if isinstance(call[0][0], CacheWrite)
    ]
    assert len(write_event) == 1

    result = cache_provider.get("SourceAgent", "1.0", "hash123", "scenario1")
    assert result == payload

    # Verify CacheHit event
    hit_event = [
        call[0][0]
        for call in subscriber.call_args_list
        if isinstance(call[0][0], CacheHit)
    ]
    assert len(hit_event) == 1


def test_deterministic_serialization(cache_provider):
    payload1 = {"a": 1, "b": 2}
    payload2 = {"b": 2, "a": 1}

    checksum1 = cache_provider._compute_checksum(payload1)
    checksum2 = cache_provider._compute_checksum(payload2)

    assert checksum1 == checksum2


def test_checksum_validation_and_corruption_deletion(cache_provider, event_bus):
    subscriber = Mock()
    event_bus.subscribe(subscriber)

    payload = {"a": 1}
    cache_provider.set("SourceAgent", "1.0", "hash123", "scenario1", payload)

    # Manually corrupt the file
    key = cache_provider._generate_key("SourceAgent", "1.0", "hash123", "scenario1")
    filepath = Path(cache_provider.cache_dir) / f"{key}.json"

    with open(filepath, "r") as f:
        data = json.load(f)

    # Modify payload without updating checksum
    data["payload"]["a"] = 2
    with open(filepath, "w") as f:
        json.dump(data, f)

    result = cache_provider.get("SourceAgent", "1.0", "hash123", "scenario1")
    assert result is None
    assert not filepath.exists()  # Deleted due to corruption

    corrupted_events = [
        call[0][0]
        for call in subscriber.call_args_list
        if isinstance(call[0][0], CacheCorrupted)
    ]
    assert len(corrupted_events) == 1


def test_ttl_expiry(cache_provider, event_bus):
    subscriber = Mock()
    event_bus.subscribe(subscriber)

    payload = {"a": 1}
    cache_provider.set("SourceAgent", "1.0", "hash123", "scenario1", payload)

    # Manually expire the file
    key = cache_provider._generate_key("SourceAgent", "1.0", "hash123", "scenario1")
    filepath = Path(cache_provider.cache_dir) / f"{key}.json"

    with open(filepath, "r") as f:
        data = json.load(f)

    past_time = datetime.now(timezone.utc) - timedelta(hours=2)
    data["metadata"]["expires_at"] = past_time.isoformat()
    with open(filepath, "w") as f:
        json.dump(data, f)

    result = cache_provider.get("SourceAgent", "1.0", "hash123", "scenario1")
    assert result is None
    assert not filepath.exists()

    expired_events = [
        call[0][0]
        for call in subscriber.call_args_list
        if isinstance(call[0][0], CacheExpired)
    ]
    assert len(expired_events) == 1


def test_schema_mismatch(cache_provider, event_bus):
    subscriber = Mock()
    event_bus.subscribe(subscriber)

    payload = {"a": 1}
    cache_provider.set("SourceAgent", "1.0", "hash123", "scenario1", payload)

    key = cache_provider._generate_key("SourceAgent", "1.0", "hash123", "scenario1")
    filepath = Path(cache_provider.cache_dir) / f"{key}.json"

    with open(filepath, "r") as f:
        data = json.load(f)

    data["metadata"]["schema_version"] = "99.9"
    with open(filepath, "w") as f:
        json.dump(data, f)

    result = cache_provider.get("SourceAgent", "1.0", "hash123", "scenario1")
    assert result is None
    assert not filepath.exists()

    corrupted_events = [
        call[0][0]
        for call in subscriber.call_args_list
        if isinstance(call[0][0], CacheCorrupted)
    ]
    assert len(corrupted_events) == 1


def test_cleanup(cache_provider, event_bus):
    subscriber = Mock()
    event_bus.subscribe(subscriber)

    # Create 1 valid, 1 expired, 1 zero-byte file
    cache_provider.set("SourceAgent", "1.0", "valid", "scenario1", {"status": "ok"})
    cache_provider.set("SourceAgent", "1.0", "expired", "scenario1", {"status": "ok"})

    key_expired = cache_provider._generate_key(
        "SourceAgent", "1.0", "expired", "scenario1"
    )
    filepath_expired = Path(cache_provider.cache_dir) / f"{key_expired}.json"
    with open(filepath_expired, "r") as f:
        data = json.load(f)
    data["metadata"]["expires_at"] = (
        datetime.now(timezone.utc) - timedelta(hours=2)
    ).isoformat()
    with open(filepath_expired, "w") as f:
        json.dump(data, f)

    # Zero-byte
    key_empty = cache_provider._generate_key("SourceAgent", "1.0", "empty", "scenario1")
    filepath_empty = Path(cache_provider.cache_dir) / f"{key_empty}.json"
    filepath_empty.touch()

    cache_provider.cleanup()

    # Valid should exist, others shouldn't
    key_valid = cache_provider._generate_key("SourceAgent", "1.0", "valid", "scenario1")
    filepath_valid = Path(cache_provider.cache_dir) / f"{key_valid}.json"

    assert filepath_valid.exists()
    assert not filepath_expired.exists()
    assert not filepath_empty.exists()

    cleanup_finished = [
        call[0][0]
        for call in subscriber.call_args_list
        if isinstance(call[0][0], CacheCleanupFinished)
    ]
    assert len(cleanup_finished) == 1
    assert cleanup_finished[0].entries_removed == 2


def test_concurrent_reads_writes(cache_provider):
    payload = {"status": "concurrent"}

    def write_task(i):
        cache_provider.set("SourceAgent", f"1.{i}", "hash", "scenario1", payload)

    def read_task(i):
        cache_provider.get("SourceAgent", f"1.{i}", "hash", "scenario1")

    threads = []
    for i in range(10):
        t_w = threading.Thread(target=write_task, args=(i,))
        t_r = threading.Thread(target=read_task, args=(i,))
        threads.append(t_w)
        threads.append(t_r)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Just ensure it doesn't crash and writes completed
    for i in range(10):
        res = cache_provider.get("SourceAgent", f"1.{i}", "hash", "scenario1")
        assert res == payload


def test_circuit_breaker_integration(cache_provider):
    import httpx

    # Force circuit breaker to open
    for _ in range(5):
        cache_provider._circuit_breaker._on_failure(
            time.time(), httpx.NetworkError("test")
        )

    # Now it should be open
    result = cache_provider.get("SourceAgent", "1.0", "hash", "scenario1")
    assert result is None  # get() returns None on circuit open, swallowing exception


def test_retry_integration(temp_cache_dir, event_bus):
    provider = FilesystemCacheProvider(temp_cache_dir, event_bus=event_bus)

    # Mock read_file to fail once then succeed
    original_read = provider._read_file
    read_calls = 0

    import httpx

    def mock_read(filepath):
        nonlocal read_calls
        read_calls += 1
        if read_calls == 1:
            raise httpx.NetworkError("Transient I/O error")
        return original_read(filepath)

    provider._read_file = mock_read

    payload = {"data": "test"}
    provider.set("SourceAgent", "1.0", "hash", "scenario1", payload)

    # This should retry and succeed
    result = provider.get("SourceAgent", "1.0", "hash", "scenario1")

    assert read_calls == 2
    assert result == payload
