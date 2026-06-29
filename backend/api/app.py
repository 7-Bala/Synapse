"""FastAPI application providing the runtime transport layer for Synapse."""

import asyncio
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from observability.event_bus import EventBus
from transport.connection_manager import ConnectionManager
from transport.transport_adapter import TransportAdapter
from transport.websocket_protocol import WebSocketConnection, WebSocketTransportProtocol

logger = logging.getLogger(__name__)

# Global instances (in a real DI framework these would be injected)
event_bus = EventBus.get_instance()
connection_manager = ConnectionManager()
transport_adapter = TransportAdapter(event_bus, connection_manager)
transport_protocol = WebSocketTransportProtocol(connection_manager)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Synapse API and Transport Runtime...")
    await transport_protocol.start()
    yield
    # Shutdown
    logger.info("Shutting down Synapse API and Transport Runtime...")
    await transport_protocol.stop()

app = FastAPI(title="Synapse Mission Control API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "synapse-api"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    connection_id = str(uuid.uuid4())
    connection = WebSocketConnection(websocket, connection_id)
    
    # Register connection
    connection_manager.register(connection)
    
    try:
        while True:
            # Heartbeat or client commands
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
            else:
                logger.debug(f"Received from {connection_id}: {data}")
    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Unregister connection on cleanup
        connection_manager.unregister(connection)

@app.post("/demo/start")
async def start_demo():
    """Trigger a demo execution to test transport."""
    import asyncio
    from core.orchestrator import Orchestrator
    from observability.instrumentation import EventBusInstrumentation
    from schemas.evidence import Evidence
    
    async def run_orchestrator():
        try:
            logger.info("Starting demo orchestrator...")
            instrumentation = EventBusInstrumentation()
            # Need at least one mock agent to not fail
            class MockAgent:
                @property
                def name(self):
                    return "MockAgent"
                async def run(self, context):
                    from schemas.agent import AgentOutput
                    import asyncio
                    await asyncio.sleep(0.1)
                    return AgentOutput(agent_name="MockAgent", findings="Demo finding", confidence=0.99)
                def get_metadata(self):
                    return {"name": "MockAgent"}

            orchestrator = Orchestrator(agents=[MockAgent()], callbacks=instrumentation)
            await orchestrator.process_evidence(new_evidence=[
                Evidence(content="demo evidence", source="demo")
            ])
            logger.info("Demo orchestrator completed.")
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            
    # Fire and forget
    asyncio.create_task(run_orchestrator())
    
    return {"status": "started"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=True)
