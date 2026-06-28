"""Live Source Specialist."""

import json
from typing import Dict

from agents.live_base import LiveBaseSpecialist
from core.tick_context import TickContext


class SourceAgent(LiveBaseSpecialist):
    """Evaluates the credibility of incoming evidence."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_assessment = {}

    def build_messages(self, context: TickContext) -> list[Dict[str, str]]:
        """Builds the LLM prompt for the Source Specialist."""
        evidence_content = (
            [json.loads(ev.model_dump_json()) for ev in context.evidence_delta]
            if context.evidence_delta
            else []
        )

        prompt_template = self._prompt_loader.load(self.name, self._prompt_version)

        # Replace variables in the prompt manually for now
        system_prompt = prompt_template.replace(
            "{{EVIDENCE}}", json.dumps(evidence_content, indent=2)
        )
        system_prompt = system_prompt.replace(
            "{{PREVIOUS_ASSESSMENT}}", json.dumps(self._last_assessment, indent=2)
        )

        return [{"role": "system", "content": system_prompt}]

    async def run(self, context: TickContext):
        # We need to capture the output so we can update our last assessment
        output = await super().run(context)

        if output.confidence > 0.0:
            # We don't have the parsed LiveSpecialistOutput directly here, but we can store finding
            self._last_assessment = {
                "finding": output.findings,
                "confidence": output.confidence,
            }

        return output

    def explain(self) -> str:
        """Produces a concise human-readable explanation of the agent's state."""
        if not self._last_assessment:
            return "Source Specialist has not yet made an assessment."

        finding = self._last_assessment.get("finding", "Unknown finding")
        confidence = self._last_assessment.get("confidence", 0.0)

        return (
            f"Cross-cycle memory currently tracks a confidence of {confidence:.2f}.\n"
            f"Most recent finding: {finding}\n"
            f"Primary evidence impacts: (tracked in structured reasoning ledger)"
        )
