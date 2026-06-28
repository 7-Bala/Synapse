"""Main demo script with playback for Synapse backend Sprint 4."""

import asyncio
import os
from unittest.mock import MagicMock

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
from demo.evidence_player import EvidencePlayer, RecordingAgentWrapper
from demo.recorder import DemoRecorder
from prompts.base import PromptBuilder
from services.cerebras import CerebrasService
from validators.response_validator import ResponseValidator


class MockCerebrasResponse:
    """Helper to return dynamic mock responses for the SourceAgent during playback."""

    def __init__(self):
        self.tick_count = 0

    def mock_create(self, *args, **kwargs):
        self.tick_count += 1

        # We vary the confidence and reliability to simulate the scenario's tension curve
        if self.tick_count == 1:
            findings, conf, rel = "Unverified anonymous tip.", 0.40, "false"
        elif self.tick_count == 2:
            findings, conf, rel = "Unverified anonymous image.", 0.60, "false"
        elif self.tick_count == 3:
            findings, conf, rel = "Social media rumors causing concern.", 0.65, "false"
        elif self.tick_count == 4:
            findings, conf, rel = "Verified official incident report.", 0.85, "true"
        else:
            findings, conf, rel = "Source is a verified system sensor.", 0.95, "true"

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            f'{{"findings": "{findings}", "confidence": {conf}, "is_reliable": {rel}}}'
        )
        return mock_response


async def main() -> None:
    """Runs a full playback of the crisis scenario."""

    # 1. Initialize AI Infrastructure
    prompts_dir = os.path.join(os.path.dirname(__file__), "prompts", "system")
    prompt_builder = PromptBuilder(templates_dir=prompts_dir)
    cerebras_service = CerebrasService()
    response_validator = ResponseValidator()

    # MOCK CEREBRAS TO SUPPORT DYNAMIC SCENARIO TENSION
    mock_engine = MockCerebrasResponse()
    cerebras_service._client.chat.completions.create = mock_engine.mock_create  # type: ignore[method-assign]

    # 2. Initialize Recorder and Registry
    recorder = DemoRecorder()
    registry = AgentRegistry()

    # Helper to register and wrap
    def register_and_wrap(agent):
        wrapped = RecordingAgentWrapper(agent, recorder)
        registry.register(wrapped)

    register_and_wrap(create_vision_agent())
    register_and_wrap(create_timeline_agent())
    register_and_wrap(create_contradiction_agent())
    register_and_wrap(create_prediction_agent())
    register_and_wrap(create_consensus_agent())

    real_source_agent = SourceAgent(
        prompt_builder, cerebras_service, response_validator
    )
    register_and_wrap(real_source_agent)

    # 3. Create Orchestrator
    orchestrator = Orchestrator(agents=registry.get_all_agents())

    # 4. Setup Evidence Player
    player = EvidencePlayer(orchestrator, recorder)

    # Assuming we run from the project root `Synapse/`
    scenario_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "demo",
        "scenarios",
        "crisis_response.json",
    )
    player.load_scenario(scenario_path)

    # 5. Execute Playback
    print("\n--- Loading Profile: Supply_Chain_Flash_Crisis ---")

    # Run the player (await until completion)
    player.set_speed(10.0)  # Speed it up for tests
    await player.play()

    # 6. Output Results
    print("\n--- Final Arbitration Timeline ---")
    for update in recorder.decision_timeline:
        print(
            f"\nEvidence Cycle {update['evidence_cycle']}: {update['decision']} (Conf: {update['confidence']:.2f}, HR Required: {update['human_review_required']})"
        )
        print("  [Downstream Systems]:")
        for sys in update["downstream_systems"]:
            print(f"    - {sys['system']}: {sys['status']}")

    print(f"\nTotal Chronological Events Recorded: {len(recorder.events)}")


if __name__ == "__main__":
    asyncio.run(main())
