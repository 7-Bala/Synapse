"""Provenance engine for tracking artifact metadata."""

import datetime
import platform
import subprocess
import sys
from typing import Dict, Any


class ProvenanceEngine:
    """Collects system, runtime, and git metadata to ensure full artifact provenance."""

    def __init__(
        self,
        schema_version: str = "1.0",
        replay_version: str = "1.0",
        model_identifier: str = "llama3.1-8b",
        cache_provider: str = "FilesystemCacheProvider",
        registry_version: str = "1.0",
        settings_version: str = "1.0",
    ):
        self.schema_version = schema_version
        self.replay_version = replay_version
        self.model_identifier = model_identifier
        self.cache_provider = cache_provider
        self.registry_version = registry_version
        self.settings_version = settings_version

    def _run_git_command(self, cmd: list[str]) -> str:
        """Helper to run a git command safely."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=2
            )
            return result.stdout.strip()
        except Exception:
            return "UNKNOWN"

    def get_git_metadata(self) -> Dict[str, str]:
        """Collects git metadata. Never fails generation if unavailable."""
        commit = self._run_git_command(["git", "rev-parse", "HEAD"])
        tag = self._run_git_command(["git", "describe", "--tags", "--exact-match"])
        branch = self._run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])

        # Check dirty state
        dirty_output = self._run_git_command(["git", "status", "--porcelain"])
        is_dirty = "UNKNOWN"
        if dirty_output != "UNKNOWN":
            is_dirty = "True" if dirty_output.strip() else "False"

        return {
            "commit": commit,
            "tag": tag,
            "branch": branch,
            "is_dirty": is_dirty,
        }

    def get_runtime_metadata(self) -> Dict[str, str]:
        """Collects runtime metadata."""
        return {
            "python_version": sys.version.split()[0],
            "platform": platform.platform(),
            "hostname": platform.node(),
            "generation_timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        }

    def get_system_metadata(self) -> Dict[str, str]:
        """Collects system metadata configured during initialization."""
        return {
            "schema_version": self.schema_version,
            "replay_version": self.replay_version,
            "model_identifier": self.model_identifier,
            "cache_provider": self.cache_provider,
            "registry_version": self.registry_version,
            "settings_version": self.settings_version,
        }

    def get_all_metadata(self) -> Dict[str, Any]:
        """Returns the complete provenance bundle."""
        return {
            "git": self.get_git_metadata(),
            "runtime": self.get_runtime_metadata(),
            "system": self.get_system_metadata(),
        }
