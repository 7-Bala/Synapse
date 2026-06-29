import uuid
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from api.dependencies import get_connection_manager
from transport.connection_manager import ConnectionManager
from transport.websocket_protocol import WebSocketConnection

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    connection_manager: ConnectionManager = Depends(get_connection_manager)
):
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
