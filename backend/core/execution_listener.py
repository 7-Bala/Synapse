"""Event listener that subscribes to the EventBus to persist execution records and build the agent DAG."""

import time
import logging
from typing import Dict, Any, Optional
from observability.event_bus import EventBus
from observability.events import (
    BaseEvent, ExecutionCreated, ExecutionStarted, ExecutionCompleted, ExecutionFailed,
    AgentStarted, AgentCompleted, AgentFailed, PlannerStarted, PlannerFinished,
    ValidationStarted, ValidationCompleted, ValidationPassed, ValidationFailed, ValidationBlocked,
    ToolInvoked, ToolCompleted, ToolCallFailed
)
from core.execution_store import get_execution_store
from schemas.execution import ExecutionRecord, ExecutionState, ExecutionMode, AgentNode

logger = logging.getLogger(__name__)

class ExecutionEventListener:
    """Subscribes to EventBus and updates Execution Store state based on events."""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.store = get_execution_store()
        
        # Subscribe to EventBus
        self.event_bus.subscribe(self.handle_event)
        logger.info("ExecutionEventListener successfully subscribed to EventBus.")

    def handle_event(self, event: BaseEvent) -> None:
        """Processes a single EventBus event and transitions state/records."""
        try:
            exec_id = getattr(event, "correlation_id", None)
            if not exec_id:
                return

            # 1. Append the raw event to the execution's event log
            self.store.add_event(exec_id, event)

            # 2. Handle state transitions and record updates
            event_type = type(event).__name__
            
            # Ensure execution record exists
            record = self.store.get_execution(exec_id)
            if not record:
                # Implicitly create a default record (for tests/demo runs)
                record = ExecutionRecord(
                    id=exec_id,
                    status=ExecutionState.QUEUED,
                    createdAt=event.timestamp,
                    updatedAt=event.timestamp,
                    userPrompt="Autonomous Agent Execution",
                    executionMode=ExecutionMode.LIVE,
                    metadata={}
                )
                self.store.create_execution(record)

            # Process state transitions
            if event_type == "ExecutionCreated":
                # Already handled by default creation, but update timestamp
                record.updatedAt = event.timestamp
                self.store.update_execution(record)

            elif event_type == "ExecutionStarted":
                self.store.update_execution_status(exec_id, ExecutionState.RUNNING)

            elif event_type == "PlannerStarted":
                self.store.update_execution_status(exec_id, ExecutionState.PLANNING)
                
            elif event_type == "PlannerFinished":
                # Return to running state after planning is done
                self.store.update_execution_status(exec_id, ExecutionState.RUNNING)

            elif event_type == "ValidationStarted":
                self.store.update_execution_status(exec_id, ExecutionState.VALIDATING)

            elif event_type == "ValidationCompleted" or event_type == "ValidationPassed":
                # Return to running or completed depending on status
                pass

            elif event_type == "ExecutionCompleted":
                self.store.update_execution_status(exec_id, ExecutionState.COMPLETED)

            elif event_type == "ExecutionFailed":
                record.metadata["error"] = getattr(event, "error", "Unknown error")
                self.store.update_execution(record)
                self.store.update_execution_status(exec_id, ExecutionState.FAILED)

            # Process Agent DAG Node updates
            elif event_type == "AgentStarted":
                agent_id = getattr(event, "agent_id", "")
                # Format a unique node ID based on execution and agent_id
                node_id = f"{exec_id}_{agent_id}"
                
                # Check if node exists
                nodes = self.store.get_agent_nodes(exec_id)
                existing = next((n for n in nodes if n.id == node_id), None)
                
                # Determine parent/children
                parent_id = None
                if nodes:
                    # In a tick lifecycle, the parent is the last active node, or None
                    parent_id = nodes[-1].id
                
                if existing:
                    existing.status = "RUNNING"
                    self.store.update_agent_node(exec_id, existing)
                else:
                    node = AgentNode(
                        id=node_id,
                        name=agent_id,
                        role="Specialist Agent",
                        model="default-model",
                        status="RUNNING",
                        parentId=parent_id
                    )
                    self.store.add_agent_node(exec_id, node)
                    
                    # Update parent's children list
                    if parent_id:
                        parent_node = next((n for n in nodes if n.id == parent_id), None)
                        if parent_node and node_id not in parent_node.childrenIds:
                            parent_node.childrenIds.append(node_id)
                            self.store.update_agent_node(exec_id, parent_node)

                record.currentAgent = agent_id
                record.updatedAt = event.timestamp
                self.store.update_execution(record)

            elif event_type == "AgentCompleted":
                agent_id = getattr(event, "agent_id", "")
                node_id = f"{exec_id}_{agent_id}"
                nodes = self.store.get_agent_nodes(exec_id)
                node = next((n for n in nodes if n.id == node_id), None)
                if node:
                    node.status = "COMPLETED"
                    node.latency = getattr(event, "latency_ms", 0)
                    node.output = getattr(event, "result_reference", None)
                    # Simulated metrics
                    node.tokenUsage = 1500
                    node.confidence = 0.95
                    self.store.update_agent_node(exec_id, node)
                    
                    # Accumulate metrics to execution record
                    record.totalLatency += node.latency
                    record.totalTokens += node.tokenUsage
                    record.estimatedCost += (node.tokenUsage / 1000) * 0.002
                
                record.updatedAt = event.timestamp
                self.store.update_execution(record)

            elif event_type == "AgentFailed":
                agent_id = getattr(event, "agent_id", "")
                node_id = f"{exec_id}_{agent_id}"
                nodes = self.store.get_agent_nodes(exec_id)
                node = next((n for n in nodes if n.id == node_id), None)
                if node:
                    node.status = "FAILED"
                    node.output = getattr(event, "error", "Agent execution failed")
                    self.store.update_agent_node(exec_id, node)
                
                record.updatedAt = event.timestamp
                self.store.update_execution(record)

        except Exception as e:
            logger.error(f"Error in ExecutionEventListener handling event: {e}", exc_info=True)

# Global initialization helper
_listener_instance: Optional[ExecutionEventListener] = None

def initialize_execution_listener(event_bus: EventBus) -> ExecutionEventListener:
    global _listener_instance
    if _listener_instance is None or _listener_instance.event_bus != event_bus:
        _listener_instance = ExecutionEventListener(event_bus)
    return _listener_instance
