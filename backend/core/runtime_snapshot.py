"""RuntimeSnapshotService — computes live snapshot summaries of the execution runtime.

This service gathers metrics from the ExecutionScheduler, ExecutionStore,
and any active orchestrators. It does not store or duplicate state.
"""

import time
from typing import Any, Dict, List
from core.execution_store import get_execution_store
from core.scheduler import get_scheduler
from core.execution_orchestrator import _active_orchestrators
from schemas.execution import ExecutionState, ExecutionRecord, TimelineEntry

class RuntimeSnapshotService:
    """Read-only service to snapshot the current state of the execution runtime."""

    @staticmethod
    def get_snapshot() -> Dict[str, Any]:
        store = get_execution_store()
        scheduler = get_scheduler()
        
        all_executions = store.list_executions()
        
        active_count = 0
        queued_count = 0
        completed_count = 0
        failed_count = 0
        cancelled_count = 0
        
        total_tokens = 0
        estimated_cost = 0.0
        total_completed_latency = 0
        completed_latencies_count = 0
        
        for r in all_executions:
            # Categorize status
            if r.status in (ExecutionState.INITIALIZING, ExecutionState.PLANNING, ExecutionState.RUNNING, ExecutionState.VALIDATING):
                active_count += 1
            elif r.status == ExecutionState.QUEUED:
                queued_count += 1
            elif r.status == ExecutionState.COMPLETED:
                completed_count += 1
            elif r.status == ExecutionState.FAILED:
                failed_count += 1
            elif r.status == ExecutionState.CANCELLED:
                cancelled_count += 1
                
            # Totals
            total_tokens += r.totalTokens
            estimated_cost += r.estimatedCost
            
            # Latency for completed
            if r.status == ExecutionState.COMPLETED and r.totalLatency > 0:
                total_completed_latency += r.totalLatency
                completed_latencies_count += 1
                
        avg_latency_ms = 0.0
        if completed_latencies_count > 0:
            avg_latency_ms = total_completed_latency / completed_latencies_count
            
        # Success rate: completed / (completed + failed + cancelled)
        total_terminal = completed_count + failed_count + cancelled_count
        success_rate = 1.0
        if total_terminal > 0:
            success_rate = completed_count / total_terminal
            
        # Running agents count: count how many orchestrators have currentAgent set
        running_agents_count = 0
        active_orchestrator_list = list(_active_orchestrators.values())
        for orch in active_orchestrator_list:
            record = store.get_execution(orch._execution_id)
            if record and record.currentAgent:
                running_agents_count += 1
                
        # Queue depth
        queue_len = scheduler.queue_depth
        
        return {
            "activeExecutions": active_count,
            "queuedExecutions": queued_count,
            "completedExecutions": completed_count,
            "failedExecutions": failed_count,
            "cancelledExecutions": cancelled_count,
            "queueLength": queue_len,
            "schedulerWorkers": scheduler._max_concurrent,
            "runningAgents": running_agents_count,
            "successRate": success_rate,
            "averageLatency": avg_latency_ms / 1000.0, # convert to seconds
            "totalTokens": total_tokens,
            "estimatedCost": estimated_cost
        }

    @staticmethod
    def get_active_executions() -> List[Dict[str, Any]]:
        store = get_execution_store()
        all_executions = store.list_executions()
        active = []
        for r in all_executions:
            if r.status in (ExecutionState.INITIALIZING, ExecutionState.PLANNING, ExecutionState.RUNNING, ExecutionState.VALIDATING):
                elapsed = 0.0
                if r.startedAt:
                    elapsed = time.time() - r.startedAt
                elif r.createdAt:
                    elapsed = time.time() - r.createdAt
                active.append({
                    "id": r.id,
                    "status": r.status,
                    "userPrompt": r.userPrompt,
                    "currentAgent": r.currentAgent or "N/A",
                    "progress": r.progress,
                    "elapsed": elapsed,
                    "executionMode": r.executionMode
                })
        return active

    @staticmethod
    def get_queued_executions() -> List[Dict[str, Any]]:
        store = get_execution_store()
        all_executions = store.list_executions()
        queued = []
        # Find queued ones. Position in list_executions() or queue can be estimated.
        # Since list_executions is sorted by createdAt desc, reverse it or sort by asc to get queue position.
        queued_records = [r for r in all_executions if r.status == ExecutionState.QUEUED]
        queued_records.sort(key=lambda x: x.createdAt) # oldest first (FIFO order)
        
        for idx, r in enumerate(queued_records):
            waiting_time = time.time() - r.createdAt
            queued.append({
                "id": r.id,
                "position": idx + 1,
                "waitingTime": waiting_time,
                "executionMode": r.executionMode,
                "userPrompt": r.userPrompt
            })
        return queued

    @staticmethod
    def get_active_agents() -> List[Dict[str, Any]]:
        """Scans active execution orchestrators and gathers details about running specialist agents."""
        store = get_execution_store()
        active_agents = []
        active_orchestrator_list = list(_active_orchestrators.values())
        for orch in active_orchestrator_list:
            r = store.get_execution(orch._execution_id)
            if not r or r.status not in (ExecutionState.INITIALIZING, ExecutionState.PLANNING, ExecutionState.RUNNING, ExecutionState.VALIDATING):
                continue
            if r.currentAgent:
                # Find the running agent node in the DAG to get details
                nodes = store.get_agent_nodes(orch._execution_id)
                agent_node = next((n for n in nodes if n.name == r.currentAgent and n.status == "RUNNING"), None)
                
                latency = 0
                tokens = 0
                retry_count = 0
                
                if agent_node:
                    latency = agent_node.latency
                    tokens = agent_node.tokenUsage
                    retry_count = agent_node.retryCount
                
                active_agents.append({
                    "agentName": r.currentAgent,
                    "executionId": r.id,
                    "status": "RUNNING",
                    "tokens": tokens,
                    "latency": latency,
                    "retryCount": retry_count
                })
        return active_agents

    @staticmethod
    def get_events_feed(limit: int = 50) -> List[Dict[str, Any]]:
        """Gathers the latest events/timeline entries across all executions, sorted newest first."""
        store = get_execution_store()
        all_executions = store.list_executions()
        feed: List[Dict[str, Any]] = []
        for r in all_executions:
            timeline = store.get_timeline(r.id)
            for entry in timeline:
                feed.append({
                    "executionId": r.id,
                    "timestamp": entry.timestamp,
                    "event": entry.event,
                    "detail": entry.detail,
                    "agent": entry.agent
                })
        # Sort by timestamp descending
        feed.sort(key=lambda x: x["timestamp"], reverse=True)
        return feed[:limit]

    @staticmethod
    def get_health() -> Dict[str, Any]:
        scheduler = get_scheduler()
        # We check basic statuses
        # Scheduler status: ok if running
        scheduler_status = "GREEN" if scheduler._running else "RED"
        # EventBus is a singleton; get_instance should work
        try:
            from observability.event_bus import EventBus
            bus = EventBus.get_instance()
            bus_status = "GREEN" if bus._enabled else "YELLOW"
        except Exception:
            bus_status = "RED"
            
        # Store status
        try:
            store = get_execution_store()
            store.list_executions()
            store_status = "GREEN"
        except Exception:
            store_status = "RED"
            
        active_count = 0
        all_executions = get_execution_store().list_executions()
        for r in all_executions:
            if r.status in (ExecutionState.INITIALIZING, ExecutionState.PLANNING, ExecutionState.RUNNING, ExecutionState.VALIDATING):
                active_count += 1
                
        # Overall status is RED if scheduler/store is RED, YELLOW if anything is YELLOW or warning, else GREEN
        overall = "GREEN"
        if scheduler_status == "RED" or store_status == "RED":
            overall = "RED"
        elif bus_status == "YELLOW":
            overall = "YELLOW"
            
        return {
            "overall": overall,
            "scheduler": scheduler_status,
            "eventBus": bus_status,
            "store": store_status,
            "queueDepth": scheduler.queue_depth,
            "workerCount": scheduler._max_concurrent,
            "activeExecutionCount": active_count
        }
