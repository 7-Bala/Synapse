"""Mission Control API router for real-time operational dashboard visualization and control."""

import logging
from typing import Any, Dict, List
from fastapi import APIRouter
from core.runtime_snapshot import RuntimeSnapshotService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/mission-control", tags=["mission-control"])


@router.get("/overview", response_model=Dict[str, Any])
async def get_overview():
    """Retrieve operational statistics and aggregated totals."""
    return RuntimeSnapshotService.get_snapshot()


@router.get("/runtime", response_model=List[Dict[str, Any]])
async def get_active_executions():
    """Retrieve details of executions currently active in the lifecycle."""
    return RuntimeSnapshotService.get_active_executions()


@router.get("/queued", response_model=List[Dict[str, Any]])
async def get_queued_executions():
    """Retrieve details of executions in the FIFO scheduler queue."""
    return RuntimeSnapshotService.get_queued_executions()


@router.get("/active-agents", response_model=List[Dict[str, Any]])
async def get_active_agents():
    """Retrieve details of specialist agents currently running."""
    return RuntimeSnapshotService.get_active_agents()


@router.get("/events", response_model=List[Dict[str, Any]])
async def get_events_feed():
    """Retrieve a unified recent timeline/event feed across all executions."""
    return RuntimeSnapshotService.get_events_feed()


@router.get("/health", response_model=Dict[str, Any])
async def get_health():
    """Retrieve structured health states of system components."""
    return RuntimeSnapshotService.get_health()
