"""Real SourceAgent backed by Cerebras."""

from agents.base import BaseAgent
from core.tick_context import TickContext
from prompts.base import PromptBuilder
from prompts.source import SourceResponse
from schemas.agent import AgentOutput
from services.cerebras import CerebrasService
from validators.response_validator import ResponseValidator


class SourceAgent(BaseAgent):
    """An AI-powered agent that verifies the reliability of evidence sources."""

    def __init__(
        self,
        prompt_builder: PromptBuilder,
        cerebras_service: CerebrasService,
        response_validator: ResponseValidator,
    ):
        """Initializes the agent with its infrastructure dependencies."""
        self._prompt_builder = prompt_builder
        self._cerebras_service = cerebras_service
        self._response_validator = response_validator

    @property
    def name(self) -> str:
        """Returns the agent name."""
        return "SourceAgent"

    async def run(self, context: TickContext) -> AgentOutput:
        """Executes the AI logic to analyze evidence sources."""
        if not context.evidence_delta:
            return AgentOutput(
                agent_name=self.name,
                confidence=1.0,
                findings="No new evidence to verify.",
            )

        # For Sprint 3, analyze the first piece of evidence
        evidence = context.evidence_delta[0]

        # 1. PromptBuilder
        messages = self._prompt_builder.build_messages(
            template_filename="source.md",
            variables={
                "evidence_text": evidence.content,
                "evidence_source": evidence.source,
            },
        )

        # 2. CerebrasService
        raw_response = self._cerebras_service.generate_structured_response(
            messages=messages, response_format={"type": "json_object"}
        )

        # 3. ResponseValidator
        validation_result = self._response_validator.validate(
            response_text=raw_response, schema=SourceResponse
        )

        if not validation_result.is_valid or not validation_result.data:
            return AgentOutput(
                agent_name=self.name,
                confidence=0.0,
                findings=f"Failed to produce valid output: {validation_result.error}",
            )

        parsed_data = validation_result.data
        return AgentOutput(
            agent_name=self.name,
            confidence=parsed_data.confidence,
            findings=f"{parsed_data.findings} (Reliable: {parsed_data.is_reliable})",
        )
