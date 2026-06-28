"""Cerebras AI service infrastructure."""

import os
from typing import Any, Dict, List, Optional

from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv


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

    def generate_structured_response(
        self,
        messages: List[Dict[str, str]],
        response_format: Any = None,
        timeout_seconds: float = 10.0,
        max_retries: int = 3,
    ) -> Optional[str]:
        """Calls the Cerebras API to generate a structured output.

        Args:
            messages: The provider-ready message dictionaries.
            response_format: Optional structured output schema/format.
            timeout_seconds: Timeout for the API call.
            max_retries: Number of retry attempts.

        Returns:
            str: The raw JSON string returned by the model, or None if failed.
        """
        for attempt in range(max_retries):
            try:
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
            except Exception:
                # In a real system, we might log the exception `e` here.
                if attempt == max_retries - 1:
                    return None
        return None
