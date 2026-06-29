"""Configuration settings for Synapse."""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralized configuration via pydantic-settings."""

    # Provider & Model
    cerebras_api_key: Optional[str] = None
    default_model: str = "llama3.1-8b"

    # Timeouts & Retries
    llm_timeout_seconds: float = 10.0
    llm_max_retries: int = 3
    retry_base_delay_ms: float = 1000.0
    retry_max_delay_ms: float = 10000.0
    retry_jitter_enabled: bool = True

    # Circuit Breaker
    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_success_threshold: int = 2
    circuit_breaker_sliding_window_seconds: float = 60.0
    circuit_breaker_recovery_timeout_seconds: float = 30.0
    circuit_breaker_half_open_max_requests: int = 3
    circuit_breaker_half_open_success_threshold: int = 2

    # Storage Paths
    base_dir: str = "/Users/bala/Documents/Synapse"
    cache_dir: str = "/Users/bala/Documents/Synapse/.cache"
    artifacts_dir: str = "/Users/bala/Documents/Synapse/artifacts"
    golden_dir: str = "/Users/bala/Documents/Synapse/backend/golden"
    metrics_dir: str = "/Users/bala/Documents/Synapse/backend/observability/metrics"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
