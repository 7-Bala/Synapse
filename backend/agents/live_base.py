"""Abstract base class for all live specialists."""

import hashlib
from typing import Dict, Type

from agents.base import BaseAgent
from core.confidence_engine import compute_confidence
from core.pipeline_state import PipelineState
from core.tick_context import TickContext
from observability.event_bus import EventBus
from observability.events import (
    SpecialistStarted,
    SpecialistFinished,
    LLMRequestStarted,
    LLMRequestFinished,
    CacheLookupStarted,
    CacheLookupFinished,
    CacheHit,
    CacheMiss,
    ValidationStarted,
    ValidationFinished,
)
from schemas.agent import AgentOutput, LiveSpecialistOutput, SpecialistStatus
from cache.provider import CacheProvider
from services.cerebras import CerebrasService
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
        cache_manager: CacheProvider,
        pipeline_state: PipelineState,
    ):
        self._name = name
        self._prompt_version = prompt_version
        self._prompt_loader = prompt_loader
        self._cerebras_service = cerebras_service
        self._cache_manager = cache_manager
        self._pipeline_state = pipeline_state
        self._event_bus = EventBus.get_instance()

    @property
    def name(self) -> str:
        return self._name

    def _get_schema(self) -> Type[LiveSpecialistOutput]:
        """Returns the uniform schema."""
        return LiveSpecialistOutput

    def build_messages(self, context: TickContext) -> list[Dict[str, str]]:
        """Must be implemented by subclasses to build LLM messages."""
        raise NotImplementedError

    def get_metadata(self) -> dict:
        """Returns provenance metadata for the agent."""
        return {
            "name": self.name,
            "version": "1.0",
            "implementation_version": "1.0",
            "prompt_version": self._prompt_version,
            "schema_version": "1.0",
        }

    async def run(self, context: TickContext) -> AgentOutput:
        """Executes the live specialist pipeline."""

        self._event_bus.emit(
            SpecialistStarted(
                correlation_id=str(context.tick_id),
                specialist=self.name,
                evidence_cycle=context.tick_id,
            )
        )

        evidence_content = (
            [ev.content for ev in context.evidence_delta]
            if context.evidence_delta
            else []
        )
        evidence_str = "".join(evidence_content)
        evidence_hash = hashlib.sha256(evidence_str.encode("utf-8")).hexdigest()
        scenario = self._pipeline_state.scenario_name

        # 1. Check Cache
        self._event_bus.emit(
            CacheLookupStarted(
                correlation_id=str(context.tick_id), specialist=self.name
            )
        )

        cached_data = self._cache_manager.get(
            self.name, self._prompt_version, evidence_hash, scenario
        )

        self._event_bus.emit(
            CacheLookupFinished(
                correlation_id=str(context.tick_id), specialist=self.name
            )
        )

        if cached_data:
            self._event_bus.emit(
                CacheHit(correlation_id=str(context.tick_id), specialist=self.name)
            )
            self._pipeline_state.completed_specialists.add(self.name)
            confidence = compute_confidence(
                cached_data["confidence_reason"], cached_data["finding"]
            )

            self._event_bus.emit(
                SpecialistFinished(
                    correlation_id=str(context.tick_id),
                    specialist=self.name,
                    evidence_cycle=context.tick_id,
                    status=cached_data["status"],
                    confidence=confidence,
                )
            )

            return AgentOutput(
                agent_name=self.name,
                confidence=confidence,
                findings=cached_data["finding"],
            )

        self._event_bus.emit(
            CacheMiss(correlation_id=str(context.tick_id), specialist=self.name)
        )

        # 2. Build Request
        messages = self.build_messages(context)

        # 3. Call Cerebras
        self._event_bus.emit(
            LLMRequestStarted(
                correlation_id=str(context.tick_id),
                specialist=self.name,
                prompt_version=self._prompt_version,
            )
        )

        try:
            raw_response = self._cerebras_service.generate_structured_response(
                messages=messages, response_format={"type": "json_object"}
            )

            self._event_bus.emit(
                LLMRequestFinished(
                    correlation_id=str(context.tick_id),
                    specialist=self.name,
                    status="SUCCESS",
                    tokens_in=0,  # Telemetry extraction omitted for brevity
                    tokens_out=0,
                )
            )
        except Exception:
            raw_response = None
            self._event_bus.emit(
                LLMRequestFinished(
                    correlation_id=str(context.tick_id),
                    specialist=self.name,
                    status="ERROR",
                    tokens_in=0,
                    tokens_out=0,
                )
            )

        # 4. Validate Structured Output
        self._event_bus.emit(
            ValidationStarted(correlation_id=str(context.tick_id), specialist=self.name)
        )

        parsed = None
        if raw_response:
            parsed = StructuredOutputValidator.validate(
                raw_response, self._get_schema()
            )

        self._event_bus.emit(
            ValidationFinished(
                correlation_id=str(context.tick_id),
                specialist=self.name,
                success=bool(parsed),
            )
        )

        if not parsed:
            # Fallback to FAILED (Execution/Parsing Failure)
            self._pipeline_state.failed_specialists.add(self.name)

            self._event_bus.emit(
                SpecialistFinished(
                    correlation_id=str(context.tick_id),
                    specialist=self.name,
                    evidence_cycle=context.tick_id,
                    status=SpecialistStatus.FAILED.value,
                    confidence=0.0,
                )
            )

            return AgentOutput(
                agent_name=self.name,
                confidence=0.0,
                findings="Execution failed. Platform health issue.",
            )

        # 5. Overwrite tracking fields on parsed
        parsed.specialist = self.name
        parsed.prompt_version = self._prompt_version
        parsed.cache_hit = False
        parsed.latency_ms = 0  # Handled by EventBus now out of band

        # 6. Cache the valid result
        self._cache_manager.set(
            self.name,
            self._prompt_version,
            evidence_hash,
            scenario,
            parsed.model_dump(),
        )

        # 7. Metrics
        self._pipeline_state.completed_specialists.add(self.name)
        confidence = compute_confidence(parsed.confidence_reason, parsed.finding)

        self._event_bus.emit(
            SpecialistFinished(
                correlation_id=str(context.tick_id),
                specialist=self.name,
                evidence_cycle=context.tick_id,
                status=parsed.status.value,
                confidence=confidence,
            )
        )

        return AgentOutput(
            agent_name=self.name, confidence=confidence, findings=parsed.finding
        )
