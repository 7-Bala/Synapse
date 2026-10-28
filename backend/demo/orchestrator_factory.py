from typing import List, Optional
import asyncio

from core.orchestrator import Orchestrator
from observability.instrumentation import EventBusInstrumentation
from agents.base import BaseAgent
from schemas.agent import AgentOutput
from core.tick_context import TickContext


class MockAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "MockAgent"

    async def run(self, context: TickContext) -> AgentOutput:
        await asyncio.sleep(0.1)
        return AgentOutput(agent_name="MockAgent", findings="Demo finding", confidence=0.99)


def create_demo_orchestrator(instrumentation: EventBusInstrumentation, execution_id: Optional[str] = None) -> Orchestrator:
    """Creates a demo orchestrator populated with mock agents for testing the transport layer."""
    return Orchestrator(agents=[MockAgent()], callbacks=instrumentation, execution_id=execution_id)
