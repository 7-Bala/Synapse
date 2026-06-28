"""Main demo script for Synapse backend Sprint 3."""

import asyncio
import os
from unittest.mock import MagicMock
from uuid import uuid4

from agents.source import SourceAgent
from agents.stub_agents import (
    create_consensus_agent,
    create_contradiction_agent,
    create_prediction_agent,
    create_timeline_agent,
    create_vision_agent,
)
from core.agent_registry import AgentRegistry
from core.orchestrator import Orchestrator
from prompts.base import PromptBuilder
from schemas.evidence import Evidence
from services.cerebras import CerebrasService
from validators.response_validator import ResponseValidator


async def main() -> None:
    """Runs a simulated three-tick execution of the Synapse backend."""

    # 1. Initialize AI Infrastructure
    prompts_dir = os.path.join(os.path.dirname(__file__), "prompts", "system")
    prompt_builder = PromptBuilder(templates_dir=prompts_dir)
    cerebras_service = CerebrasService()
    response_validator = ResponseValidator()

    # MOCK CEREBRAS FOR SMOKE TEST
    # We mock it here so the end-to-end pipeline passes without a real API key.
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = (
        '{"findings": "Source is a verified system sensor.", "confidence": 0.95, "is_reliable": true}'
    )
    cerebras_service._client.chat.completions.create = MagicMock(return_value=mock_response)  # type: ignore[method-assign]

    # 2. Initialize Agent Registry
    registry = AgentRegistry()

    # Register stubs
    registry.register(create_vision_agent())
    registry.register(create_timeline_agent())
    registry.register(create_contradiction_agent())
    registry.register(create_prediction_agent())
    registry.register(create_consensus_agent())

    # Register real SourceAgent
    real_source_agent = SourceAgent(
        prompt_builder=prompt_builder,
        cerebras_service=cerebras_service,
        response_validator=response_validator,
    )
    registry.register(real_source_agent)

    # 3. Create Orchestrator
    orchestrator = Orchestrator(agents=registry.get_all_agents())

    # 4. Simulate Ticks
    evidence_items = [
        ("System logs show no anomalies", "Sensor Reading"),
        ("Network packet received on port 80", "Network Packet"),
        ("User submitted the form", "User Input"),
    ]

    for tick_index, (content, source) in enumerate(evidence_items, start=1):
        print(f"\n{'='*50}")
        print(f"Starting Tick {tick_index}")
        print(f"{'='*50}")

        # Inject fake evidence
        new_evidence = Evidence(id=uuid4(), content=content, source=source)
        print(f"Injected Evidence: {new_evidence.content} (from {new_evidence.source})")

        # Run tick
        consensus = await orchestrator.process_evidence([new_evidence])

        # Print Agent Outputs for this tick
        print("\n--- Agent Outputs ---")
        entries = orchestrator._blackboard.entries_for_tick(tick_index)
        for entry in entries:
            print(
                f"[{entry.agent_name}]: {entry.output.findings} (Conf: {entry.output.confidence:.2f})"
            )

        # Print Consensus
        print("\n--- Consensus ---")
        print(f"Decision: {consensus.decision}")
        print(f"Confidence: {consensus.confidence:.2f}")
        print(f"Explanation: {consensus.explanation}")
        print(f"Human Review Required: {consensus.human_review_required}")

        # Print Blackboard Size
        blackboard_size = len(orchestrator._blackboard.get_all())
        print("\n--- Blackboard State ---")
        print(f"Total entries in blackboard: {blackboard_size}")


if __name__ == "__main__":
    asyncio.run(main())
