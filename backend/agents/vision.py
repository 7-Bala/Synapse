"""Live Vision Specialist."""

import json
from typing import Dict

from agents.live_base import LiveBaseSpecialist
from core.tick_context import TickContext


class VisionAgent(LiveBaseSpecialist):
    """Evaluates physical evidence to establish facts."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_state = {}

    def build_messages(self, context: TickContext) -> list[Dict[str, str]]:
        """Builds the LLM prompt for the Vision Specialist."""
        evidence_content = (
            [json.loads(ev.model_dump_json()) for ev in context.evidence_delta]
            if context.evidence_delta
            else []
        )

        prompt_template = self._prompt_loader.load(self.name, self._prompt_version)
        system_prompt = prompt_template.replace(
            "{{EVIDENCE}}", json.dumps(evidence_content, indent=2)
        )

        return [{"role": "system", "content": system_prompt}]

    async def run(self, context: TickContext):
        output = await super().run(context)

        if output.confidence > 0.0:
            self._last_state = {
                "finding": output.findings,
                "confidence": output.confidence,
                "uncertainty_hint": "Captured in reasoning.",
            }

        return output

    def explain(self) -> str:
        """Produces a concise human-readable explanation of the agent's state."""
        if not self._last_state:
            return "Vision Specialist has not yet made an assessment."

        finding = self._last_state.get("finding", "Unknown finding")
        confidence = self._last_state.get("confidence", 0.0)

        return (
            f"Physical evidence confidence is {confidence:.2f}.\n"
            f"Strongest observation: {finding}\n"
            f"Largest uncertainty: Analyzed and logged in graph.\n"
            f"Most important contradiction: Handled in structured reasoning."
        )
