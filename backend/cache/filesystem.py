"""Cache manager for specialist outputs."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional

from .provider import CacheProvider


class FilesystemCacheProvider(CacheProvider):
    """Manages independent caching per specialist using the local filesystem."""

    def __init__(self, cache_dir: str):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_key(
        self, specialist: str, prompt_version: str, evidence_hash: str, scenario: str
    ) -> str:
        """Generates a unique cache key for a specific specialist execution."""
        key_str = f"{specialist}:{prompt_version}:{evidence_hash}:{scenario}"
        return hashlib.sha256(key_str.encode("utf-8")).hexdigest()

    def get(
        self, specialist: str, prompt_version: str, evidence_hash: str, scenario: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieves a cached output if it exists."""
        key = self._generate_key(specialist, prompt_version, evidence_hash, scenario)
        filepath = self.cache_dir / f"{key}.json"

        if filepath.exists():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return None
        return None

    def set(
        self,
        specialist: str,
        prompt_version: str,
        evidence_hash: str,
        scenario: str,
        data: Dict[str, Any],
    ) -> None:
        """Caches a successful specialist output."""
        key = self._generate_key(specialist, prompt_version, evidence_hash, scenario)
        filepath = self.cache_dir / f"{key}.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)
