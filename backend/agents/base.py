"""Base agent interface for the Synapse backend."""

import abc

from core.tick_context import TickContext
from schemas.agent import AgentOutput


class BaseAgent(abc.ABC):
    """Abstract base class for all Synapse agents."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Returns the name of the agent."""
        pass

    @abc.abstractmethod
    async def run(self, context: TickContext) -> AgentOutput:
        """Executes the agent's logic for a single tick.

        Args:
            context: The immutable TickContext containing all necessary state.

        Returns:
            AgentOutput: The structured output from the agent.
        """
        pass

    @abc.abstractmethod
    def get_metadata(self) -> dict:
        """Returns provenance metadata for the agent."""
        pass
