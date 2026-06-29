import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from .dependencies import transport_protocol

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Synapse API and Transport Runtime...")
    await transport_protocol.start()
    yield
    # Shutdown
    logger.info("Shutting down Synapse API and Transport Runtime...")
    await transport_protocol.stop()
