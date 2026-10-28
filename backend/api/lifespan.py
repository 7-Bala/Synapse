import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from .dependencies import transport_protocol
from core.scheduler import get_scheduler

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Synapse API and Transport Runtime...")
    await transport_protocol.start()
    scheduler = get_scheduler()
    await scheduler.start()
    logger.info("ExecutionScheduler started")
    yield
    # Shutdown
    logger.info("Shutting down Synapse API and Transport Runtime...")
    await scheduler.stop()
    await transport_protocol.stop()
