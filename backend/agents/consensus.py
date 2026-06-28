"""Live Consensus Arbitration Engine."""

import hashlib
import json
from typing import Dict, Any

from agents.live_base import LiveBaseSpecialist
from core.tick_context import TickContext


class ConsensusAgent(LiveBaseSpecialist):
    """Performs deterministic arbitration across all specialist outputs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_state = {}

    def _collect_specialist_outputs(
        self, evidence_hash: str, scenario: str
    ) -> Dict[str, Any]:
        """Collects the cached outputs of all previous specialists for the current tick."""
        specialists = [
            "SourceAgent",
            "VisionAgent",
            "TimelineAgent",
            "ContradictionAgent",
            "PredictionAgent",
        ]
        outputs = {}
        for sp in specialists:
            # Assuming all use "v1" prompt for now, could be dynamic
            cached = self._cache_manager.get(sp, "v1", evidence_hash, scenario)
            if cached:
                outputs[sp] = cached
            else:
                outputs[sp] = {
                    "status": "FAILED",
                    "finding": "Execution failed. Platform health issue.",
                }
        return outputs

    def _compute_deterministic_state(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Applies deterministic weighting to specialist outputs to reach a decision."""
        # Simple deterministic weighting model
        # Source (0.2), Vision (0.2), Timeline (0.2), Consistency (0.2), Simulation (0.2)

        failed_count = sum(
            1 for out in outputs.values() if out.get("status") == "FAILED"
        )

        if failed_count > 0:
            return {
                "decision": "SYSTEM_FAILURE",
                "confidence": 0.0,
                "human_review_required": False,
                "dominant_factor": "Platform health issue",
                "blocking_reason": "Required specialist execution failed",
                "specialist_breakdown": outputs,
            }

        uncertain_count = sum(
            1 for out in outputs.values() if out.get("status") == "UNCERTAIN"
        )

        confidence = 1.0 - (uncertain_count * 0.2)

        human_review_required = uncertain_count >= 2
        decision = "Hold" if human_review_required else "Publish"

        dominant_factor = (
            "Simulation recommendation"
            if not human_review_required
            else "Missing/Uncertain evidence"
        )
        blocking_reason = (
            "Too many uncertain specialists" if human_review_required else "None"
        )

        return {
            "decision": decision,
            "confidence": max(0.0, confidence),
            "human_review_required": human_review_required,
            "dominant_factor": dominant_factor,
            "blocking_reason": blocking_reason,
            "specialist_breakdown": outputs,
        }

    def build_messages(self, context: TickContext) -> list[Dict[str, str]]:
        """Builds the LLM prompt for the Consensus Specialist."""
        evidence_content = (
            [ev.content for ev in context.evidence_delta]
            if context.evidence_delta
            else []
        )
        evidence_str = "".join(evidence_content)
        evidence_hash = hashlib.sha256(evidence_str.encode("utf-8")).hexdigest()
        scenario = self._pipeline_state.scenario_name

        outputs = self._collect_specialist_outputs(evidence_hash, scenario)
        deterministic_state = self._compute_deterministic_state(outputs)

        # If systemic failure, we don't even need LLM explanation, but we'll instruct it to pass through
        if deterministic_state.get("decision") == "SYSTEM_FAILURE":
            return [
                {
                    "role": "system",
                    "content": "You are the Consensus Engine. System failure detected. Output finding: 'Arbitration could not be performed because required specialist execution failed.' Status MUST be 'FAILED'. Reason MUST be 'Platform health issue'.",
                }
            ]

        prompt_template = self._prompt_loader.load(self.name, self._prompt_version)
        system_prompt = prompt_template.replace(
            "{{DETERMINISTIC_STATE}}", json.dumps(deterministic_state, indent=2)
        )

        return [{"role": "system", "content": system_prompt}]

    async def run(self, context: TickContext):
        output = await super().run(context)

        if output.confidence >= 0.0:
            self._last_state = {
                "finding": output.findings,
                "confidence": output.confidence,
                "arbitration_hint": "Detailed in reasoning.",
            }

        return output

    def explain(self) -> str:
        """Produces a concise human-readable explanation of the agent's state."""
        if not self._last_state:
            return "Consensus Specialist has not yet made an assessment."

        finding = self._last_state.get("finding", "Unknown state")
        confidence = self._last_state.get("confidence", 0.0)

        return (
            f"Final Arbitration confidence is {confidence:.2f}.\n"
            f"Decision summary: {finding}\n"
            f"Machine Output: Logged in structured JSON trace.\n"
            f"Decision Trace: Captured in markdown reasoning.\n"
            f"Human Review Required: Reflected in arbitration breakdown."
        )
