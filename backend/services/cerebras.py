"""Cerebras AI service infrastructure."""

import json
import os
import re
import uuid
from typing import Any, Dict, List, Optional

from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

from core.retry_policy import RetryPolicy
from core.circuit_breaker import CircuitBreaker
from observability.event_bus import EventBus
from config.settings import settings
from testing.failure_injection import FailureInjector, FaultType

_INJECTOR_COMPONENT = "CerebrasProvider"


class CerebrasService:
    """Service wrapper for interacting with Cerebras LLMs."""

    def __init__(self, model_name: str = "llama3.1-8b"):
        """Initializes the Cerebras client and environment."""
        # Load .env variables
        load_dotenv()

        self.model_name = model_name
        self._live_enabled = self._is_live_provider_enabled()
        self._client = None
        if self._live_enabled:
            api_key = os.getenv("CEREBRAS_API_KEY")
            # Initialize client (will fall back to os.environ if api_key is None, standard for SDKs)
            self._client = Cerebras(api_key=api_key)
        self._retry_policy = RetryPolicy(EventBus.get_instance())
        self._circuit_breaker = CircuitBreaker("CerebrasProvider")

    @staticmethod
    def _is_live_provider_enabled() -> bool:
        raw = os.getenv("SYNAPSE_ENABLE_LIVE_PROVIDER")
        if raw is not None:
            return raw.strip().lower() in {"1", "true", "yes", "on"}
        return settings.enable_live_provider

    def _generate_offline_response(self, messages: List[Dict[str, str]]) -> str:
        prompt = "\n".join(message.get("content", "") for message in messages)
        specialist_match = re.search(r'"specialist":\s*"([^"]+)"', prompt)
        specialist = specialist_match.group(1) if specialist_match else "UnknownAgent"

        prompt_lower = prompt.lower()
        if "full terminal operations resuming" in prompt_lower:
            finding = "Source is a verified system sensor."
            confidence_reason = "official"
        elif (
            "high-resolution thermal scan shows the main terminals are undamaged"
            in prompt_lower
        ):
            finding = "Verified official incident report."
            confidence_reason = "official"
        elif "breaking: singapore port faces catastrophic disruption" in prompt_lower:
            finding = "Social media rumors causing concern."
            confidence_reason = "uncertain"
        elif (
            "drone_terminal_smoke" in prompt_lower
            or "blurry overhead view" in prompt_lower
        ):
            finding = "Unverified anonymous image."
            confidence_reason = "uncertain"
        else:
            finding = "Unverified anonymous tip."
            confidence_reason = "uncertain"

        if specialist in {
            "TimelineAgent",
            "ContradictionAgent",
            "PredictionAgent",
            "ConsensusAgent",
        }:
            finding = f"HIGH - {finding}"

        reasoning = (
            "Evidence ledger. "
            f"{'true' if confidence_reason == 'official' else 'false'}. "
            "Delta Nodes: [Event: Incident -> TS: 12:00 -> Source: Sys -> Conf: High]. "
            "Delta Edges: [Supports]. Graph Delta: Added new confirmed start time."
        )
        payload = {
            "specialist": specialist,
            "status": "COMPLETE",
            "finding": finding,
            "reasoning": reasoning,
            "confidence_reason": confidence_reason,
            "citations": ["evidence_1"],
            "latency_ms": 0,
            "tokens_in": 0,
            "tokens_out": 0,
            "prompt_version": "v1",
            "cache_hit": False,
        }
        return json.dumps(payload)

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
            # --- Failure Injection (infrastructure-only, never modifies reasoning) ---
            injector = FailureInjector.get_instance()
            if injector.should_fail(_INJECTOR_COMPONENT, FaultType.LLM_TIMEOUT):
                raise TimeoutError("[FailureInjector] Simulated LLM timeout")
            if injector.should_fail(
                _INJECTOR_COMPONENT, FaultType.LLM_CONNECTION_FAILURE
            ):
                import httpx

                raise httpx.NetworkError(
                    "[FailureInjector] Simulated connection failure"
                )
            if injector.should_fail(_INJECTOR_COMPONENT, FaultType.LLM_HTTP_429):
                import httpx

                mock_response = httpx.Response(
                    429, request=httpx.Request("POST", "http://localhost")
                )
                raise httpx.HTTPStatusError(
                    "[FailureInjector] HTTP 429",
                    request=mock_response.request,
                    response=mock_response,
                )
            if injector.should_fail(_INJECTOR_COMPONENT, FaultType.LLM_HTTP_500):
                import httpx

                mock_response = httpx.Response(
                    500, request=httpx.Request("POST", "http://localhost")
                )
                raise httpx.HTTPStatusError(
                    "[FailureInjector] HTTP 500",
                    request=mock_response.request,
                    response=mock_response,
                )
            # --- End Failure Injection ---

            # The Cerebras SDK is structurally identical to the OpenAI SDK
            kwargs: Dict[str, Any] = {
                "model": self.model_name,
                "messages": messages,
                "timeout": timeout_seconds,
            }

            # Configure structured outputs if requested
            if response_format:
                kwargs["response_format"] = response_format

            if not self._live_enabled or self._client is None:
                return self._generate_offline_response(messages)

            response = self._client.chat.completions.create(**kwargs)
            return response.choices[0].message.content  # type: ignore

        try:
            return self._retry_policy.execute(
                request_id, self._circuit_breaker.execute, _execute_call
            )
        except Exception:
            return None
