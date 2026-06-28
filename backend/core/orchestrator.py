"""Orchestrator implementation for the Synapse backend."""

import asyncio
from typing import List, Optional

from agents.base import BaseAgent
from core.blackboard import Blackboard
from core.tick_context import TickContext
from schemas.agent import AgentOutput
from schemas.blackboard import BlackboardEntry
from schemas.consensus import ConsensusOutput
from schemas.evidence import Evidence


class Orchestrator:
    """Manages the execution lifecycle for the Synapse backend."""

    def __init__(self, agents: List[BaseAgent], timeout_seconds: float = 5.0):
        """Initializes the Orchestrator.

        Args:
            agents: A list of agents to run during each tick.
            timeout_seconds: Maximum time allowed for agents to complete their tick.
        """
        self._agents = agents
        self._timeout_seconds = timeout_seconds
        self._blackboard = Blackboard()
        self._previous_consensus: Optional[ConsensusOutput] = None

        # Start ticks at 1
        self._current_tick_id = 1

    async def process_evidence(self, new_evidence: List[Evidence]) -> ConsensusOutput:
        """Processes new evidence by running a complete tick lifecycle.

        Args:
            new_evidence: A list of new Evidence objects to process.

        Returns:
            ConsensusOutput: The final consensus decision for this tick.
        """
        # 1. Create Context
        context = self._create_tick(new_evidence)

        # 2. Run Agents concurrently
        agent_outputs = await self._run_agents(context)

        # 3. Collect Results (handled implicitly in _run_agents, but separated conceptually if needed)
        valid_outputs = self._collect_results(agent_outputs)

        # 4. Append to Blackboard
        self._append_blackboard(context.tick_id, valid_outputs)

        # 5. Run Consensus
        consensus_output = self._run_consensus(context.tick_id, valid_outputs)

        # 6. Finalize Tick
        self._finalize_tick(consensus_output)

        return consensus_output

    def _create_tick(self, new_evidence: List[Evidence]) -> TickContext:
        """Creates the immutable context for the current tick."""
        context = TickContext(
            tick_id=self._current_tick_id,
            evidence_delta=new_evidence,
            blackboard_snapshot=self._blackboard.snapshot(),
            previous_consensus=self._previous_consensus,
        )
        return context

    async def _run_agents(self, context: TickContext) -> List[AgentOutput]:
        """Runs all agents concurrently and handles timeouts."""
        tasks = [agent.run(context) for agent in self._agents]

        try:
            # wait for all tasks to complete, or timeout
            results = await asyncio.wait_for(
                asyncio.gather(*tasks), timeout=self._timeout_seconds
            )
            return list(results)
        except asyncio.TimeoutError:
            # In a real system, we might handle partial results here (quorum)
            # For Sprint 1, we just return whatever finished or handle it gracefully.
            # Here we assume a strict timeout fails the gather,
            # to handle partial we would use asyncio.wait.
            # For a more robust implementation of timeout + quorum:
            return []

    def _collect_results(self, agent_outputs: List[AgentOutput]) -> List[AgentOutput]:
        """Filters and validates agent outputs before appending to the blackboard."""
        # Future-proofing: Here we could check signatures, validate schemas strictly, etc.
        return [out for out in agent_outputs if out is not None]

    def _append_blackboard(
        self, tick_id: int, agent_outputs: List[AgentOutput]
    ) -> None:
        """Appends the collected outputs to the blackboard."""
        for output in agent_outputs:
            entry = BlackboardEntry(
                tick_id=tick_id, agent_name=output.agent_name, output=output
            )
            self._blackboard.append(entry)

    def _run_consensus(
        self, tick_id: int, agent_outputs: List[AgentOutput]
    ) -> ConsensusOutput:
        """Runs the consensus logic to determine the final decision."""
        from core.consensus import run_minimal_consensus

        return run_minimal_consensus(agent_outputs)

    def _finalize_tick(self, consensus_output: ConsensusOutput) -> None:
        """Finalizes the tick by updating orchestrator state."""
        self._previous_consensus = consensus_output
        self._current_tick_id += 1
