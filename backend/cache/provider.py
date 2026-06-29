"""Cache abstraction."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class CacheProvider(ABC):
    """Abstract interface for specialist caches."""

    @abstractmethod
    def get(
        self, specialist: str, prompt_version: str, hash_key: str, scenario: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a cached response."""
        pass

    @abstractmethod
    def set(
        self,
        specialist: str,
        prompt_version: str,
        hash_key: str,
        scenario: str,
        data: Dict[str, Any],
    ) -> None:
        """Store a response in the cache."""
        pass
