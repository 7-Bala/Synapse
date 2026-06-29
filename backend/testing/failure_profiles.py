"""Deterministic failure injection profiles for Synapse infrastructure testing.

Profiles are composable: combine them using compose_profiles().
All profiles follow the same pattern:
    List[FaultConfig] that are passed to FailureInjector.enable().
"""

from typing import List

from testing.failure_injection import FaultConfig, FaultType

# ---------------------------------------------------------------------------
# Individual profiles
# ---------------------------------------------------------------------------


def provider_timeout(times: int = 1) -> List[FaultConfig]:
    """Simulates LLM provider timeout on the CerebrasProvider."""
    return [
        FaultConfig(
            component="CerebrasProvider",
            fault_type=FaultType.LLM_TIMEOUT,
            times=times,
        )
    ]


def provider_connection_failure(times: int = 1) -> List[FaultConfig]:
    """Simulates a connection error reaching the LLM provider."""
    return [
        FaultConfig(
            component="CerebrasProvider",
            fault_type=FaultType.LLM_CONNECTION_FAILURE,
            times=times,
        )
    ]


def provider_http_429(times: int = 1) -> List[FaultConfig]:
    """Simulates HTTP 429 Too Many Requests from the LLM provider."""
    return [
        FaultConfig(
            component="CerebrasProvider",
            fault_type=FaultType.LLM_HTTP_429,
            times=times,
        )
    ]


def provider_http_500(times: int = 1) -> List[FaultConfig]:
    """Simulates HTTP 500 Server Error from the LLM provider."""
    return [
        FaultConfig(
            component="CerebrasProvider",
            fault_type=FaultType.LLM_HTTP_500,
            times=times,
        )
    ]


def provider_offline(times: int = -1) -> List[FaultConfig]:
    """Simulates a completely offline LLM provider (persistent until reset)."""
    return [
        FaultConfig(
            component="CerebrasProvider",
            fault_type=FaultType.LLM_CONNECTION_FAILURE,
            times=times,
        )
    ]


def cache_corruption(times: int = 1) -> List[FaultConfig]:
    """Simulates returning corrupted data from the cache."""
    return [
        FaultConfig(
            component="FilesystemCache",
            fault_type=FaultType.CACHE_CORRUPTION,
            times=times,
        )
    ]


def cache_checksum_failure(times: int = 1) -> List[FaultConfig]:
    """Simulates a checksum mismatch when reading a cache entry."""
    return [
        FaultConfig(
            component="FilesystemCache",
            fault_type=FaultType.CACHE_CHECKSUM_FAILURE,
            times=times,
        )
    ]


def cache_expired(times: int = 1) -> List[FaultConfig]:
    """Simulates a forcibly expired cache entry."""
    return [
        FaultConfig(
            component="FilesystemCache",
            fault_type=FaultType.CACHE_EXPIRED,
            times=times,
        )
    ]


def cache_read_failure(times: int = 1) -> List[FaultConfig]:
    """Simulates a read I/O error on the cache."""
    return [
        FaultConfig(
            component="FilesystemCache",
            fault_type=FaultType.CACHE_READ_FAILURE,
            times=times,
        )
    ]


def cache_write_failure(times: int = 1) -> List[FaultConfig]:
    """Simulates a write I/O error on the cache."""
    return [
        FaultConfig(
            component="FilesystemCache",
            fault_type=FaultType.CACHE_WRITE_FAILURE,
            times=times,
        )
    ]


def retry_exhausted(times: int = 1) -> List[FaultConfig]:
    """Forces the RetryPolicy to exhaust all attempts."""
    return [
        FaultConfig(
            component="RetryPolicy",
            fault_type=FaultType.RETRY_EXHAUSTION,
            times=times,
        )
    ]


def circuit_open(times: int = 1) -> List[FaultConfig]:
    """Forces the CircuitBreaker into OPEN state."""
    return [
        FaultConfig(
            component="CircuitBreaker",
            fault_type=FaultType.CIRCUIT_FORCE_OPEN,
            times=times,
        )
    ]


def circuit_half_open(times: int = 1) -> List[FaultConfig]:
    """Forces the CircuitBreaker into HALF_OPEN state."""
    return [
        FaultConfig(
            component="CircuitBreaker",
            fault_type=FaultType.CIRCUIT_FORCE_HALF_OPEN,
            times=times,
        )
    ]


def artifact_write_failure(times: int = 1) -> List[FaultConfig]:
    """Simulates an interrupted file write during artifact staging."""
    return [
        FaultConfig(
            component="ArtifactWriter",
            fault_type=FaultType.ARTIFACT_WRITE_INTERRUPTION,
            times=times,
        )
    ]


def artifact_commit_failure(times: int = 1) -> List[FaultConfig]:
    """Simulates an interrupted commit (promotion from staging to current)."""
    return [
        FaultConfig(
            component="ArtifactWriter",
            fault_type=FaultType.ARTIFACT_COMMIT_INTERRUPTION,
            times=times,
        )
    ]


def recovery_failure(times: int = 1) -> List[FaultConfig]:
    """Simulates the RecoveryManager failing to restore a valid artifact."""
    return [
        FaultConfig(
            component="RecoveryManager",
            fault_type=FaultType.RECOVERY_FAILURE,
            times=times,
        )
    ]


def disk_full(times: int = 1) -> List[FaultConfig]:
    """Simulates a disk-full condition (OSError: No space left on device)."""
    return [
        FaultConfig(
            component="Filesystem",
            fault_type=FaultType.DISK_FULL,
            times=times,
        )
    ]


def permission_denied(times: int = 1) -> List[FaultConfig]:
    """Simulates a permission denied error on filesystem operations."""
    return [
        FaultConfig(
            component="Filesystem",
            fault_type=FaultType.PERMISSION_DENIED,
            times=times,
        )
    ]


def missing_prompt(times: int = 1) -> List[FaultConfig]:
    """Simulates a missing prompt template."""
    return [
        FaultConfig(
            component="PromptLoader",
            fault_type=FaultType.MISSING_PROMPT,
            times=times,
        )
    ]


def invalid_schema(times: int = 1) -> List[FaultConfig]:
    """Simulates an invalid prompt schema being returned."""
    return [
        FaultConfig(
            component="PromptLoader",
            fault_type=FaultType.INVALID_PROMPT_SCHEMA,
            times=times,
        )
    ]


def replay_corruption(times: int = 1) -> List[FaultConfig]:
    """Simulates a corrupted replay artifact (invalid manifest or content)."""
    return [
        FaultConfig(
            component="ReplayValidator",
            fault_type=FaultType.REPLAY_CORRUPTION,
            times=times,
        )
    ]


def eventbus_subscriber_failure(times: int = 1) -> List[FaultConfig]:
    """Simulates an EventBus subscriber raising an exception."""
    return [
        FaultConfig(
            component="EventBus",
            fault_type=FaultType.EVENTBUS_SUBSCRIBER_FAILURE,
            times=times,
        )
    ]


# ---------------------------------------------------------------------------
# Composite profiles
# ---------------------------------------------------------------------------


def compose_profiles(*profile_lists: List[FaultConfig]) -> List[FaultConfig]:
    """Combines multiple profiles into a single composable fault list."""
    combined: List[FaultConfig] = []
    for profile in profile_lists:
        combined.extend(profile)
    return combined


# ---------------------------------------------------------------------------
# Pre-built scenario profiles
# ---------------------------------------------------------------------------


def scenario_transient_provider_failure() -> List[FaultConfig]:
    """Provider fails twice then recovers — tests retry behavior."""
    return compose_profiles(
        provider_timeout(times=2),
    )


def scenario_cache_miss_and_regenerate() -> List[FaultConfig]:
    """Cache corruption forces regeneration via the LLM."""
    return compose_profiles(
        cache_corruption(times=1),
    )


def scenario_disk_full_with_recovery() -> List[FaultConfig]:
    """Disk full on first write — tests artifact writer rollback."""
    return compose_profiles(
        disk_full(times=1),
    )


def scenario_circuit_cascade() -> List[FaultConfig]:
    """Repeated provider failures trip the circuit breaker."""
    return compose_profiles(
        provider_http_500(times=5),
        circuit_open(times=1),
    )


def scenario_full_infrastructure_stress() -> List[FaultConfig]:
    """All infrastructure layers fail once — maximum stress test."""
    return compose_profiles(
        provider_timeout(times=1),
        cache_corruption(times=1),
        artifact_write_failure(times=1),
        disk_full(times=1),
        eventbus_subscriber_failure(times=1),
    )
