"""Abstract base class for all live specialists."""

import hashlib
from datetime import datetime
from typing import Dict, Type

from agents.base import BaseAgent
from core.confidence_engine import compute_confidence
from core.pipeline_state import PipelineState
from core.tick_context import TickContext
from schemas.agent import AgentOutput, LiveSpecialistOutput, SpecialistStatus
from services.cache_manager import CacheManager
from services.cerebras import CerebrasService
from services.latency_tracker import LatencyTracker
from services.metrics_logger import SpecialistMetrics
from services.prompt_loader import PromptLoader
from services.structured_output import StructuredOutputValidator


class LiveBaseSpecialist(BaseAgent):
    """Reusable abstract base class for all live specialists."""

    def __init__(
        self,
        name: str,
        prompt_version: str,
        prompt_loader: PromptLoader,
        cerebras_service: CerebrasService,
        cache_manager: CacheManager,
        pipeline_state: PipelineState,
    ):
        self._name = name
        self._prompt_version = prompt_version
        self._prompt_loader = prompt_loader
        self._cerebras_service = cerebras_service
        self._cache_manager = cache_manager
        self._pipeline_state = pipeline_state
        self._latency_tracker = LatencyTracker()

    @property
    def name(self) -> str:
        return self._name

    def _get_schema(self) -> Type[LiveSpecialistOutput]:
        """Returns the uniform schema."""
        return LiveSpecialistOutput

    def build_messages(self, context: TickContext) -> list[Dict[str, str]]:
        """Must be implemented by subclasses to build LLM messages."""
        raise NotImplementedError

    async def run(self, context: TickContext) -> AgentOutput:
        """Executes the live specialist pipeline."""
        started_at = datetime.utcnow().isoformat() + "Z"
        self._latency_tracker.start("total")

        evidence_content = (
            [ev.content for ev in context.evidence_delta]
            if context.evidence_delta
            else []
        )
        evidence_str = "".join(evidence_content)
        evidence_hash = hashlib.sha256(evidence_str.encode("utf-8")).hexdigest()

        scenario = self._pipeline_state.scenario_name

        # 1. Check Cache
        cached_data = self._cache_manager.get(
            self.name, self._prompt_version, evidence_hash, scenario
        )

        if cached_data:
            latency = self._latency_tracker.stop("total")

            # Record Metrics
            metrics = SpecialistMetrics(
                specialist=self.name,
                started_at=started_at,
                finished_at=datetime.utcnow().isoformat() + "Z",
                latency_ms=latency,
                tokens_in=0,
                tokens_out=0,
                cache_hit=True,
                status=cached_data["status"],
            )
            self._pipeline_state.metrics.setdefault(str(context.tick_id), []).append(
                metrics
            )
            self._pipeline_state.completed_specialists.add(self.name)

            # Reconstruct and compute deterministic confidence
            confidence = compute_confidence(
                cached_data["confidence_reason"], cached_data["finding"]
            )

            return AgentOutput(
                agent_name=self.name,
                confidence=confidence,
                findings=cached_data["finding"],
            )

        # 2. Build Request
        messages = self.build_messages(context)

        # 3. Call Cerebras
        self._latency_tracker.start("llm")
        # In a real app we'd await an async call. Here Cerebras is synchronous wrapper for now,
        # but normally we'd run in an executor if it blocks.
        raw_response = self._cerebras_service.generate_structured_response(
            messages=messages, response_format={"type": "json_object"}
        )
        llm_latency = self._latency_tracker.stop("llm")

        # 4. Validate Structured Output
        parsed = StructuredOutputValidator.validate(raw_response, self._get_schema())

        total_latency = self._latency_tracker.stop("total")
        finished_at = datetime.utcnow().isoformat() + "Z"

        if not parsed:
            # Fallback to uncertain
            metrics = SpecialistMetrics(
                specialist=self.name,
                started_at=started_at,
                finished_at=finished_at,
                latency_ms=total_latency,
                tokens_in=0,  # Could pull from API response if accessible
                tokens_out=0,
                cache_hit=False,
                status=SpecialistStatus.UNCERTAIN.value,
            )
            self._pipeline_state.metrics.setdefault(str(context.tick_id), []).append(
                metrics
            )
            self._pipeline_state.failed_specialists.add(self.name)

            return AgentOutput(
                agent_name=self.name,
                confidence=0.0,
                findings="Validation failed. Output uncertain.",
            )

        # 5. Overwrite tracking fields on parsed
        parsed.specialist = self.name
        parsed.prompt_version = self._prompt_version
        parsed.latency_ms = llm_latency
        parsed.cache_hit = False

        # 6. Cache the valid result
        self._cache_manager.set(
            self.name,
            self._prompt_version,
            evidence_hash,
            scenario,
            parsed.model_dump(),
        )

        # 7. Metrics
        metrics = SpecialistMetrics(
            specialist=self.name,
            started_at=started_at,
            finished_at=finished_at,
            latency_ms=total_latency,
            tokens_in=0,
            tokens_out=0,
            cache_hit=False,
            status=parsed.status.value,
        )
        self._pipeline_state.metrics.setdefault(str(context.tick_id), []).append(
            metrics
        )
        self._pipeline_state.completed_specialists.add(self.name)

        # 8. Compute Confidence & Return Standardized Output
        confidence = compute_confidence(parsed.confidence_reason, parsed.finding)

        return AgentOutput(
            agent_name=self.name, confidence=confidence, findings=parsed.finding
        )
