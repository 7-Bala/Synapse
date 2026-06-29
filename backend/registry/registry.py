"""Explicit deterministic registry for all Synapse reasoning specialists."""

from typing import Dict, List

from agents.base import BaseAgent
from agents.source import SourceAgent
from agents.vision import VisionAgent
from agents.timeline import TimelineAgent
from agents.consistency import ConsistencyAgent
from agents.simulation import ScenarioSimulationAgent
from agents.consensus import ConsensusAgent


class SpecialistRegistry:
    """Explicit deterministic registry that discovers specialists through static configuration."""

    def __init__(
        self,
        prompt_loader,
        cerebras_service,
        cache_manager,
        pipeline_state,
    ):
        self._prompt_loader = prompt_loader
        self._cerebras_service = cerebras_service
        self._cache_manager = cache_manager
        self._pipeline_state = pipeline_state

        self._agents: Dict[str, BaseAgent] = {}
        self._order: List[str] = []

        self._initialize_specialists()

    def register(self, agent: BaseAgent) -> None:
        """Registers a specialist."""
        self._agents[agent.name] = agent
        self._order.append(agent.name)

    def _initialize_specialists(self) -> None:
        """Explicitly initialize all specialists in exact order without dynamic magic."""

        # We explicitly list the types and names here
        specialist_configs = [
            (SourceAgent, "SourceAgent"),
            (VisionAgent, "VisionAgent"),
            (TimelineAgent, "TimelineAgent"),
            (ConsistencyAgent, "ContradictionAgent"),
            (ScenarioSimulationAgent, "PredictionAgent"),
            (ConsensusAgent, "ConsensusAgent"),
        ]

        for cls, name in specialist_configs:
            agent = cls(
                name=name,
                prompt_version="v1",
                prompt_loader=self._prompt_loader,
                cerebras_service=self._cerebras_service,
                cache_manager=self._cache_manager,
                pipeline_state=self._pipeline_state,
            )
            self.register(agent)

    def get_specialist(self, name: str) -> BaseAgent:
        """Retrieves a specific specialist."""
        if name not in self._agents:
            raise KeyError(f"Specialist '{name}' not found.")
        return self._agents[name]

    def get_all_specialists(self) -> List[BaseAgent]:
        """Returns all specialists in registration order."""
        return [self._agents[name] for name in self._order]
