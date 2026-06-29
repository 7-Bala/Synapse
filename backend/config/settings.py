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
