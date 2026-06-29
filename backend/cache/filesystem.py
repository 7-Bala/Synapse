"""Cache manager for specialist outputs."""

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from config.settings import settings
from core.circuit_breaker import CircuitBreaker
from core.retry_policy import RetryPolicy
from observability.event_bus import EventBus
from observability.events import (
    CacheCleanupFinished,
    CacheCleanupStarted,
    CacheCorrupted,
    CacheDelete,
    CacheExpired,
    CacheHit,
    CacheMiss,
    CacheWrite,
)
from .provider import CacheProvider
from testing.failure_injection import FailureInjector, FaultType

_INJECTOR_COMPONENT = "FilesystemCache"


class FilesystemCacheProvider(CacheProvider):
    """Manages independent caching per specialist using the local filesystem.

    Hardened for production use with metadata envelopes, checksum validation,
    TTL enforcement, versioning, automated cleanup, and telemetry.
    """

    def __init__(
        self,
        cache_dir: str,
        event_bus: Optional[EventBus] = None,
        retry_policy: Optional[RetryPolicy] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.event_bus = event_bus or EventBus.get_instance()
        self.retry_policy = retry_policy or RetryPolicy(self.event_bus)
        self._circuit_breaker = circuit_breaker or CircuitBreaker("CacheProvider")

        # Configuration
        self.provider_name = "filesystem"
        self.schema_version = settings.cache_schema_version
        self.cache_version = settings.cache_version
        self.default_ttl = settings.cache_default_ttl

    def _generate_key(
        self, specialist: str, prompt_version: str, evidence_hash: str, scenario: str
    ) -> str:
        """Generates a unique cache key for a specific specialist execution."""
        key_str = f"{specialist}:{prompt_version}:{evidence_hash}:{scenario}"
        return hashlib.sha256(key_str.encode("utf-8")).hexdigest()

    def _compute_checksum(self, payload: Dict[str, Any]) -> str:
        """Computes a deterministic SHA-256 checksum of the payload."""
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
        return hashlib.sha256(serialized).hexdigest()

    def _read_file(self, filepath: Path) -> str:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def _write_file(self, filepath: Path, content: str) -> None:
        tmp_path = filepath.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        tmp_path.replace(filepath)

    def _emit(self, event_cls: Any, key: str, **kwargs: Any) -> None:
        """Helper to emit cache events with standard metadata."""
        kwargs.setdefault("ttl", self.default_ttl)
        event = event_cls(
            correlation_id=f"cache_{key}_{time.time()}",
            specialist=None,
            cache_key=key,
            provider=self.provider_name,
            cache_version=self.cache_version,
            schema_version=self.schema_version,
            **kwargs,
        )
        self.event_bus.emit(event)

    def get(  # noqa: C901
        self, specialist: str, prompt_version: str, evidence_hash: str, scenario: str
    ) -> Optional[Dict[str, Any]]:  # noqa: C901
        """Retrieves a cached output if it exists and passes all validation gates."""

        def _execute_get() -> Optional[Dict[str, Any]]:  # noqa: C901
            key = self._generate_key(
                specialist, prompt_version, evidence_hash, scenario
            )
            filepath = self.cache_dir / f"{key}.json"

            if not filepath.exists():
                self._emit(CacheMiss, key)
                return None

            # --- Failure Injection ---
            _inj = FailureInjector.get_instance()
            if _inj.should_fail(_INJECTOR_COMPONENT, FaultType.CACHE_READ_FAILURE):
                self._emit(CacheCorrupted, key)
                return None
            if _inj.should_fail(_INJECTOR_COMPONENT, FaultType.CACHE_CORRUPTION):
                filepath.unlink(missing_ok=True)
                self._emit(CacheCorrupted, key)
                return None
            if _inj.should_fail(_INJECTOR_COMPONENT, FaultType.CACHE_CHECKSUM_FAILURE):
                filepath.unlink(missing_ok=True)
                self._emit(CacheCorrupted, key)
                return None
            if _inj.should_fail(_INJECTOR_COMPONENT, FaultType.CACHE_EXPIRED):
                filepath.unlink(missing_ok=True)
                self._emit(CacheExpired, key)
                return None
            # --- End Failure Injection ---

            try:
                # 1. Read File (wrapped in RetryPolicy)
                content = self.retry_policy.execute(
                    f"cache_read_{key}", self._read_file, filepath
                )

                # 2. Parse JSON
                data = json.loads(content)
            except Exception as e:
                print(f"Exception: {repr(e)}")
                # Malformed JSON or read error
                filepath.unlink(missing_ok=True)
                self._emit(CacheCorrupted, key)
                return None

            # 3. Validate Metadata Structure
            if "metadata" not in data or "payload" not in data:
                filepath.unlink(missing_ok=True)
                self._emit(CacheCorrupted, key)
                return None

            meta = data["metadata"]
            payload = data["payload"]

            # Extract attributes safely
            entry_schema = meta.get("schema_version")
            entry_cache_ver = meta.get("cache_version")
            checksum = meta.get("checksum")
            expires_at = meta.get("expires_at")
            ttl = meta.get("ttl_seconds", self.default_ttl)

            # 4. Validate Schema Version
            if entry_schema != self.schema_version:
                filepath.unlink(missing_ok=True)
                self._emit(CacheCorrupted, key, ttl=ttl, checksum=checksum)
                return None

            # 5. Validate Cache Version
            if entry_cache_ver != self.cache_version:
                filepath.unlink(missing_ok=True)
                self._emit(CacheCorrupted, key, ttl=ttl, checksum=checksum)
                return None

            # 6. Validate TTL
            try:
                expiry_time = datetime.fromisoformat(expires_at)
                if datetime.now(timezone.utc) > expiry_time:
                    filepath.unlink(missing_ok=True)
                    self._emit(CacheExpired, key, ttl=ttl, checksum=checksum)
                    return None
            except (ValueError, TypeError):
                filepath.unlink(missing_ok=True)
                self._emit(CacheCorrupted, key, ttl=ttl, checksum=checksum)
                return None

            # 7. Validate SHA256 Checksum
            expected_checksum = self._compute_checksum(payload)
            if checksum != expected_checksum:
                filepath.unlink(missing_ok=True)
                self._emit(CacheCorrupted, key, ttl=ttl, checksum=checksum)
                return None

            self._emit(CacheHit, key, ttl=ttl, checksum=checksum)
            return payload

        try:
            return self._circuit_breaker.execute(_execute_get)
        except Exception as e:
            print(f"Exception: {repr(e)}")
            return None

    def set(
        self,
        specialist: str,
        prompt_version: str,
        evidence_hash: str,
        scenario: str,
        data: Dict[str, Any],
    ) -> None:
        """Caches a successful specialist output in a secure metadata envelope."""

        def _execute_set() -> None:
            key = self._generate_key(
                specialist, prompt_version, evidence_hash, scenario
            )
            filepath = self.cache_dir / f"{key}.json"

            checksum = self._compute_checksum(data)
            now = datetime.now(timezone.utc)

            # Configurable TTLs can be based on specialist type, but we use default for now
            ttl_seconds = self.default_ttl

            metadata = {
                "created_at": now.isoformat(),
                "expires_at": datetime.fromtimestamp(
                    now.timestamp() + ttl_seconds, timezone.utc
                ).isoformat(),
                "ttl_seconds": ttl_seconds,
                "checksum": checksum,
                "schema_version": self.schema_version,
                "cache_version": self.cache_version,
                "provider": self.provider_name,
                "generator": specialist,
            }

            envelope = {"metadata": metadata, "payload": data}

            # --- Failure Injection ---
            _inj = FailureInjector.get_instance()
            if _inj.should_fail(_INJECTOR_COMPONENT, FaultType.CACHE_WRITE_FAILURE):
                return  # silently drop the write — simulates I/O failure
            # --- End Failure Injection ---

            content = json.dumps(envelope)
            self.retry_policy.execute(
                f"cache_write_{key}", self._write_file, filepath, content
            )

            self._emit(CacheWrite, key, ttl=ttl_seconds, checksum=checksum)

        try:
            self._circuit_breaker.execute(_execute_set)
        except Exception as e:
            print(f"Exception: {repr(e)}")
            pass

    def cleanup(self) -> None:  # noqa: C901
        """Removes expired, corrupt, and zero-byte cache files deterministically."""

        def _execute_cleanup() -> None:
            if not settings.cache_cleanup_enabled:
                return

            self.event_bus.emit(
                CacheCleanupStarted(
                    correlation_id=f"cleanup_{time.time()}",
                    specialist=None,
                    provider=self.provider_name,
                )
            )

            entries_removed = 0

            # Deterministic iteration
            for filepath in sorted(self.cache_dir.glob("*.json")):
                key = filepath.stem

                if filepath.stat().st_size == 0:
                    filepath.unlink(missing_ok=True)
                    self._emit(CacheDelete, key)
                    entries_removed += 1
                    continue

                try:
                    # We don't use retry on cleanup reads to keep cleanup fast and failure-isolated
                    content = self._read_file(filepath)
                    data = json.loads(content)

                    if "metadata" not in data or "payload" not in data:
                        raise ValueError("Missing metadata")

                    meta = data["metadata"]

                    if (
                        meta.get("schema_version") != self.schema_version
                        or meta.get("cache_version") != self.cache_version
                    ):
                        raise ValueError("Version mismatch")

                    expires_at_str = meta.get("expires_at")
                    if not expires_at_str:
                        raise ValueError("Missing expires_at")

                    expires_at = datetime.fromisoformat(expires_at_str)
                    if datetime.now(timezone.utc) > expires_at:
                        filepath.unlink(missing_ok=True)
                        self._emit(
                            CacheExpired,
                            key,
                            ttl=meta.get("ttl_seconds", self.default_ttl),
                            checksum=meta.get("checksum"),
                        )
                        entries_removed += 1
                        continue

                except Exception:
                    filepath.unlink(missing_ok=True)
                    self._emit(CacheCorrupted, key)
                    entries_removed += 1

            self.event_bus.emit(
                CacheCleanupFinished(
                    correlation_id=f"cleanup_done_{time.time()}",
                    specialist=None,
                    provider=self.provider_name,
                    entries_removed=entries_removed,
                )
            )

        try:
            self._circuit_breaker.execute(_execute_cleanup)
        except Exception as e:
            print(f"Exception: {repr(e)}")
            pass
