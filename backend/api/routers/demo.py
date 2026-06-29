import asyncio
import logging
from fastapi import APIRouter

from observability.instrumentation import EventBusInstrumentation
from schemas.evidence import Evidence
from demo.orchestrator_factory import create_demo_orchestrator

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/demo/start")
async def start_demo():
    """Trigger a demo execution to test transport."""
    async def run_orchestrator():
        try:
            logger.info("Starting demo orchestrator...")
            instrumentation = EventBusInstrumentation()
            orchestrator = create_demo_orchestrator(instrumentation)
            await orchestrator.process_evidence(new_evidence=[
                Evidence(content="demo evidence", source="demo")
            ])
            logger.info("Demo orchestrator completed.")
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            
    # Fire and forget
    asyncio.create_task(run_orchestrator())
    
    return {"status": "started"}
