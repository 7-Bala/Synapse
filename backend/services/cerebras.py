"""Cerebras AI service infrastructure."""

import os
import uuid
from typing import Any, Dict, List, Optional

from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

from core.retry_policy import RetryPolicy
from core.circuit_breaker import CircuitBreaker
from observability.event_bus import EventBus
from config.settings import settings


class CerebrasService:
    """Service wrapper for interacting with Cerebras LLMs."""

    def __init__(self, model_name: str = "llama3.1-8b"):
        """Initializes the Cerebras client and environment."""
        # Load .env variables
        load_dotenv()

        api_key = os.getenv("CEREBRAS_API_KEY")
        # Initialize client (will fall back to os.environ if api_key is None, standard for SDKs)
        self._client = Cerebras(api_key=api_key)
        self.model_name = model_name
        self._retry_policy = RetryPolicy(EventBus.get_instance())
        self._circuit_breaker = CircuitBreaker("CerebrasProvider")

    def generate_structured_response(
        self,
        messages: List[Dict[str, str]],
        response_format: Any = None,
        timeout_seconds: float = settings.llm_timeout_seconds,
    ) -> Optional[str]:
        """Calls the Cerebras API to generate a structured output.

        Args:
            messages: The provider-ready message dictionaries.
            response_format: Optional structured output schema/format.
            timeout_seconds: Timeout for the API call.

        Returns:
            str: The raw JSON string returned by the model, or None if failed.
        """
        request_id = str(uuid.uuid4())

        def _execute_call() -> str:
            # The Cerebras SDK is structurally identical to the OpenAI SDK
            kwargs: Dict[str, Any] = {
                "model": self.model_name,
                "messages": messages,
                "timeout": timeout_seconds,
            }

            # Configure structured outputs if requested
            if response_format:
                kwargs["response_format"] = response_format

            response = self._client.chat.completions.create(**kwargs)
            return response.choices[0].message.content  # type: ignore

        try:
            return self._retry_policy.execute(
                request_id, self._circuit_breaker.execute, _execute_call
            )
        except Exception:
            return None
