"""API router for execution engine endpoints."""

import time
import uuid
import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.execution_store import get_execution_store
from core.execution_orchestrator import get_orchestrator
from core.scheduler import get_scheduler
from schemas.execution import ExecutionRecord, ExecutionState, ExecutionMode, AgentNode, TimelineEntry

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/executions", tags=["executions"])


@router.get("", response_model=List[ExecutionRecord])
async def list_executions():
    """Lists all executions from the store."""
    store = get_execution_store()
    return store.list_executions()


@router.get("/{execution_id}", response_model=ExecutionRecord)
async def get_execution(execution_id: str):
    """Retrieves detailed execution details."""
    store = get_execution_store()
    record = store.get_execution(execution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Execution not found")
    return record


@router.get("/{execution_id}/events", response_model=List[Dict[str, Any]])
async def get_execution_events(execution_id: str):
    """Retrieves all append-only event logs for a given execution."""
    store = get_execution_store()
    events = store.get_events(execution_id)
    serialized_events = []
    for ev in events:
        try:
            serialized_events.append(ev.model_dump())
        except Exception:
            serialized_events.append(str(ev))
    return serialized_events


@router.get("/{execution_id}/agents", response_model=List[AgentNode])
async def get_execution_agents(execution_id: str):
    """Retrieves the agent DAG hierarchy for a given execution."""
    store = get_execution_store()
    return store.get_agent_nodes(execution_id)


@router.get("/{execution_id}/timeline", response_model=List[TimelineEntry])
async def get_execution_timeline(execution_id: str):
    """Retrieves the immutable ordered timeline for a given execution."""
    store = get_execution_store()
    record = store.get_execution(execution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Execution not found")
    return store.get_timeline(execution_id)


class ExecutionRequest(BaseModel):
    prompt: str
    mode: Optional[str] = "LIVE"


@router.post("", response_model=ExecutionRecord)
async def create_execution(request: ExecutionRequest):
    """Triggers a new execution — delegates to ExecutionScheduler."""
    store = get_execution_store()
    execution_id = str(uuid.uuid4())

    # Map mode string to enum
    mode = ExecutionMode.LIVE
    if request.mode == "SIMULATION":
        mode = ExecutionMode.SIMULATION
    elif request.mode == "REPLAY":
        mode = ExecutionMode.REPLAY

    # Create Execution Record in QUEUED state
    now = time.time()
    record = ExecutionRecord(
        id=execution_id,
        status=ExecutionState.QUEUED,
        createdAt=now,
        updatedAt=now,
        userPrompt=request.prompt,
        executionMode=mode,
        metadata={},
    )
    store.create_execution(record)

    # Hand off to the scheduler — returns immediately
    scheduler = get_scheduler()
    await scheduler.enqueue(execution_id)

    logger.info("ExecutionRequest: enqueued %s (queue depth=%d)", execution_id, scheduler.queue_depth)
    return record


@router.post("/{execution_id}/cancel", response_model=ExecutionRecord)
async def cancel_execution(execution_id: str):
    """Cancels an active execution via cooperative cancellation."""
    store = get_execution_store()
    record = store.get_execution(execution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Execution not found")

    # Signal the active orchestrator if it exists
    orchestrator = get_orchestrator(execution_id)
    if orchestrator:
        orchestrator.request_cancel()
    else:
        # Already finished or not yet started — directly cancel
        if record.status not in (ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED):
            updated = store.update_execution_status(execution_id, ExecutionState.CANCELLED)
            if not updated:
                raise HTTPException(status_code=500, detail="Failed to cancel execution")

    # Return updated record
    updated_record = store.get_execution(execution_id)
    return updated_record or record
