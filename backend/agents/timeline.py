"""Live Timeline Specialist."""

import json
from typing import Dict

from agents.live_base import LiveBaseSpecialist
from core.tick_context import TickContext


class TimelineAgent(LiveBaseSpecialist):
    """Evaluates temporal consistency across evidence."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_state = {}

    def build_messages(self, context: TickContext) -> list[Dict[str, str]]:
        """Builds the LLM prompt for the Timeline Specialist."""
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
                "graph_delta_hint": "Captured in reasoning.",
            }

        return output

    def explain(self) -> str:
        """Produces a concise human-readable explanation of the agent's state."""
        if not self._last_state:
            return "Timeline Specialist has not yet made an assessment."

        finding = self._last_state.get("finding", "Unknown consistency score")
        confidence = self._last_state.get("confidence", 0.0)

        return (
            f"Temporal reasoning confidence is {confidence:.2f}.\n"
            f"Consistency Score: {finding}\n"
            f"Largest temporal inconsistency: Captured in structured graph delta.\n"
            f"Strongest causal chain: Logged in temporal graph.\n"
            f"Most important new event: Extracted as delta node."
        )
