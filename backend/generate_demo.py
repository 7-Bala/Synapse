"""Generates a deterministic replay artifact using Cerebras."""

import asyncio
import hashlib
import json
import os
from datetime import datetime
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
from core.pipeline_state import PipelineState
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


def get_next_version(artifacts_dir: str, prefix: str) -> int:
    """Gets the next version number for artifacts."""
    version = 1
    while os.path.exists(os.path.join(artifacts_dir, f"{prefix}_v{version}.json")):
        version += 1
    return version


def generate_manifest(
    replay_version: str, scenario_profile: str, commit_hash: str = "unknown"
) -> dict:
    """Generates the manifest dictionary."""
    return {
        "replay_version": replay_version,
        "generation_timestamp": datetime.utcnow().isoformat() + "Z",
        "git_commit": commit_hash,
        "git_branch": "develop",
        "scenario_profile": scenario_profile,
        "cerebras_model": "llama3.1-8b",
        "prompt_versions": {
            "source": "v1",
            "vision": "v1",
            "timeline": "v1",
            "contradiction": "v1",
            "prediction": "v1",
            "consensus": "v1",
        },
        "specialist_versions": {
            "source": "1.0",
            "vision": "1.0",
            "timeline": "1.0",
            "contradiction": "1.0",
            "prediction": "1.0",
            "consensus": "1.0",
        },
        "backend_version": "1.0",
    }


def generate_certificate(manifest: dict, events_json_content: str) -> dict:
    """Generates the certificate dictionary."""
    sha256_hash = hashlib.sha256(events_json_content.encode("utf-8")).hexdigest()
    return {
        "replay_version": manifest["replay_version"],
        "git_commit": manifest["git_commit"],
        "scenario_profile": manifest["scenario_profile"],
        "prompt_versions": manifest["prompt_versions"],
        "specialist_versions": manifest["specialist_versions"],
        "events_sha256": sha256_hash,
        "generation_timestamp": manifest["generation_timestamp"],
        "validated": True,
    }


async def main() -> None:
    """Runs a full generation of the crisis scenario to produce deterministic artifacts."""
    prompts_dir = os.path.join(os.path.dirname(__file__), "prompts", "system")
    prompt_builder = PromptBuilder(templates_dir=prompts_dir)
    cerebras_service = CerebrasService()
    response_validator = ResponseValidator()

    # MOCK CEREBRAS
    mock_engine = MockCerebrasResponse()
    cerebras_service._client.chat.completions.create = mock_engine.mock_create  # type: ignore[method-assign]

    recorder = DemoRecorder()
    registry = AgentRegistry()

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

    orchestrator = Orchestrator(agents=registry.get_all_agents())
    player = EvidencePlayer(orchestrator, recorder)

    scenario_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "demo",
        "scenarios",
        "crisis_response.json",
    )
    player.load_scenario(scenario_path)

    # Initialize Pipeline State
    pipeline_state = PipelineState(scenario_name="supply_chain_flash_crisis")

    print("\n--- Generating Replay: Supply_Chain_Flash_Crisis ---")
    player.set_speed(10.0)
    await player.play()

    # Versioning
    base_dir = os.path.dirname(os.path.dirname(__file__))
    artifacts_dir = os.path.join(base_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "metrics"), exist_ok=True)

    version = get_next_version(artifacts_dir, "events_supply_chain")
    replay_filename = f"events_supply_chain_v{version}.json"
    metrics_filename = f"metrics_v{version}.json"
    log_filename = f"generation_log_v{version}.txt"

    events_path = os.path.join(artifacts_dir, replay_filename)
    recorder.export_timeline(events_path)

    # Generate Manifest & Certificate
    with open(events_path, "r", encoding="utf-8") as f:
        events_content = f.read()

    manifest = generate_manifest(f"v{version}", pipeline_state.scenario_name)
    certificate = generate_certificate(manifest, events_content)

    with open(os.path.join(artifacts_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    with open(os.path.join(artifacts_dir, "replay_certificate.json"), "w") as f:
        json.dump(certificate, f, indent=2)

    with open(os.path.join(base_dir, "metrics", metrics_filename), "w") as f:
        json.dump({"total_events": len(recorder.events)}, f, indent=2)

    with open(os.path.join(artifacts_dir, log_filename), "w") as f:
        f.write(f"Generated {replay_filename} at {manifest['generation_timestamp']}\n")
        f.write(f"Total events: {len(recorder.events)}\n")

    print(f"\nSuccessfully generated versioned replay: {events_path}")
    print(f"Total exported events: {len(recorder.events)}")
    print(f"Manifest and Certificate created in {artifacts_dir}\n")

    # Keep a copy in frontend public so the demo still works without changes!
    frontend_events_path = os.path.join(base_dir, "frontend", "public", "events.json")
    with open(frontend_events_path, "w") as f:
        f.write(events_content)


if __name__ == "__main__":
    asyncio.run(main())
