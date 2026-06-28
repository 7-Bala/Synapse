"""Evidence player to deterministically replay scenarios."""

import asyncio
import json
from typing import Any, Dict
from uuid import uuid4

from agents.base import BaseAgent
from core.orchestrator import Orchestrator
from core.tick_context import TickContext
from demo.recorder import DemoRecorder
from schemas.agent import AgentOutput
from schemas.evidence import Evidence


class RecordingAgentWrapper(BaseAgent):
    """Wraps an agent to record its completion without modifying the Orchestrator."""

    def __init__(self, agent: BaseAgent, recorder: DemoRecorder):
        self._agent = agent
        self._recorder = recorder

    @property
    def name(self) -> str:
        return self._agent.name

    async def run(self, context: TickContext) -> AgentOutput:
        # Run the actual agent
        output = await self._agent.run(context)

        # Log completion chronologically
        self._recorder.record_agent_completion(context.tick_id, output)
        return output


class EvidencePlayer:
    """Plays back a scenario tick-by-tick."""

    def __init__(self, orchestrator: Orchestrator, recorder: DemoRecorder):
        """Initializes the EvidencePlayer.

        Note: The orchestrator's agents must have been wrapped in RecordingAgentWrapper
        to capture agent-level completion events chronologically.
        """
        from demo.downstream import DownstreamSystemSimulator

        self.orchestrator = orchestrator
        self.recorder = recorder
        self.downstream_simulator = DownstreamSystemSimulator()
        self._scenario: Dict[str, Any] = {}
        self._is_paused = False
        self._speed = 1.0
        self._current_cycle_idx = 0

    def load_scenario(self, filepath: str) -> None:
        """Loads a JSON scenario file."""
        with open(filepath, "r", encoding="utf-8") as f:
            self._scenario = json.load(f)

    def set_speed(self, speed: float) -> None:
        """Sets the playback speed multiplier."""
        self._speed = speed

    def pause(self) -> None:
        """Pauses the playback."""
        self._is_paused = True

    def resume(self) -> None:
        """Resumes the playback."""
        self._is_paused = False

    def restart(self) -> None:
        """Restarts the playback from cycle 1."""
        self._current_cycle_idx = 0
        self._is_paused = False

    async def play(self) -> None:
        """Executes the loaded scenario."""
        ticks = self._scenario.get("ticks", [])

        while self._current_cycle_idx < len(ticks):
            if self._is_paused:
                await asyncio.sleep(0.5)
                continue

            tick_data = ticks[self._current_cycle_idx]
            cycle_id = tick_data["tick_id"]

            # 1. Parse and build evidence
            evidences = []
            for ev_data in tick_data.get("evidence", []):
                ev = Evidence(
                    id=uuid4(), content=ev_data["content"], source=ev_data["source"]
                )
                evidences.append(ev)

            # 2. Record arrival
            self.recorder.record_evidence_arrival(cycle_id, evidences)

            # 3. Process through orchestrator (this triggers agent completions)
            consensus = await self.orchestrator.process_evidence(evidences)

            # 4. Simulate downstream enterprise systems
            downstream_states = self.downstream_simulator.process_cycle(
                cycle_id, consensus
            )

            # 5. Record consensus update and downstream state
            self.recorder.record_consensus_update(
                cycle_id, consensus, downstream_states
            )

            self._current_cycle_idx += 1

            # Simulate real-time gap based on playback speed
            await asyncio.sleep(1.0 / self._speed)
