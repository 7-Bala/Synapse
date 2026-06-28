"""Agent registry for the Synapse backend."""

from typing import Dict, List

from agents.base import BaseAgent


class AgentRegistry:
    """Registry for discovering and managing agents."""

    def __init__(self) -> None:
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """Registers an initialized agent instance."""
        self._agents[agent.name] = agent

    def get_agent(self, name: str) -> BaseAgent:
        """Retrieves an agent by name."""
        if name not in self._agents:
            raise KeyError(f"Agent '{name}' not found in registry.")
        return self._agents[name]

    def get_all_agents(self) -> List[BaseAgent]:
        """Returns all registered agents."""
        return list(self._agents.values())
