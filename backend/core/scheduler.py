"""ExecutionScheduler — FIFO queue with configurable concurrency for orchestrator jobs.

Responsibilities:
  - Accept execution IDs for scheduling
  - Enforce a maximum number of concurrent active executions
  - Dispatch each execution to a fresh ExecutionOrchestrator
  - Clean up the orchestrator registry when a job finishes

Usage:
    scheduler = ExecutionScheduler(max_concurrent=3)
    await scheduler.start()          # called during FastAPI lifespan startup
    await scheduler.enqueue("exec-id")
    await scheduler.stop()           # called during FastAPI lifespan shutdown
"""

import asyncio
import logging
from typing import Optional

from core.execution_orchestrator import (
    ExecutionOrchestrator,
    deregister_orchestrator,
    register_orchestrator,
)

logger = logging.getLogger(__name__)


class ExecutionScheduler:
    """FIFO execution scheduler with bounded concurrency."""

    def __init__(self, max_concurrent: int = 3) -> None:
        self._max_concurrent = max_concurrent
        self._queue: asyncio.Queue = asyncio.Queue()
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._worker_task: Optional[asyncio.Task] = None
        self._running = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the background worker loop. Call once during app startup."""
        if self._running:
            return
        self._running = True
        # Create a fresh queue bound to the current running loop
        self._queue = asyncio.Queue()
        self._semaphore = asyncio.Semaphore(self._max_concurrent)
        self._worker_task = asyncio.create_task(
            self._worker_loop(), name="ExecutionScheduler.worker"
        )
        logger.info("ExecutionScheduler started (max_concurrent=%d)", self._max_concurrent)


    async def stop(self) -> None:
        """Gracefully stop the scheduler. Call during app shutdown."""
        self._running = False
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except (asyncio.CancelledError, Exception):
                pass
        logger.info("ExecutionScheduler stopped")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def enqueue(self, execution_id: str) -> None:
        """Add an execution to the scheduling queue."""
        logger.info("ExecutionScheduler: enqueuing %s", execution_id)
        await self._queue.put(execution_id)

    @property
    def queue_depth(self) -> int:
        """Returns the number of executions waiting in the queue."""
        return self._queue.qsize()

    # ------------------------------------------------------------------
    # Worker Loop
    # ------------------------------------------------------------------

    async def _worker_loop(self) -> None:
        """Continuously pulls from the queue and dispatches executions."""
        while self._running:
            try:
                try:
                    execution_id = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                assert self._semaphore is not None
                await self._semaphore.acquire()

                asyncio.get_event_loop().create_task(
                    self._run_execution(execution_id),
                    name=f"ExecutionScheduler.run.{execution_id}",
                )

            except asyncio.CancelledError:
                break
            except Exception as exc:  # noqa: BLE001
                logger.error("ExecutionScheduler worker error: %s", exc, exc_info=True)

    async def _run_execution(self, execution_id: str) -> None:
        """Creates and runs an orchestrator for a single execution."""
        orchestrator = ExecutionOrchestrator(execution_id=execution_id)
        register_orchestrator(execution_id, orchestrator)
        try:
            logger.info("ExecutionScheduler: starting orchestrator for %s", execution_id)
            await orchestrator.start_execution()
        except asyncio.CancelledError:
            logger.info("ExecutionScheduler: execution %s cancelled", execution_id)
        except Exception as exc:  # noqa: BLE001
            logger.error("ExecutionScheduler: execution %s crashed: %s", execution_id, exc, exc_info=True)
        finally:
            deregister_orchestrator(execution_id)
            assert self._semaphore is not None
            self._semaphore.release()


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_scheduler_instance: Optional[ExecutionScheduler] = None


def get_scheduler() -> ExecutionScheduler:
    """Returns the global ExecutionScheduler singleton."""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = ExecutionScheduler(max_concurrent=3)
    return _scheduler_instance
