"""Main demo script for Synapse backend Sprint 1."""

import asyncio
from uuid import uuid4

from agents.stub_agents import (
    create_consensus_agent,
    create_contradiction_agent,
    create_prediction_agent,
    create_source_agent,
    create_timeline_agent,
    create_vision_agent,
)
from core.orchestrator import Orchestrator
from schemas.evidence import Evidence


async def main() -> None:
    """Runs a simulated three-tick execution of the Synapse backend."""
    # 1. Initialize agents
    agents = [
        create_vision_agent(),
        create_source_agent(),
        create_timeline_agent(),
        create_contradiction_agent(),
        create_prediction_agent(),
        create_consensus_agent(),
    ]

    # 2. Create Orchestrator
    orchestrator = Orchestrator(agents=agents)

    # 3. Simulate Ticks
    evidence_items = [
        ("Evidence A", "User Input"),
        ("Evidence B", "Sensor Reading"),
        ("Evidence C", "Network Packet"),
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

        # Print Blackboard Size
        blackboard_size = len(orchestrator._blackboard.get_all())
        print("\n--- Blackboard State ---")
        print(f"Total entries in blackboard: {blackboard_size}")


if __name__ == "__main__":
    asyncio.run(main())
