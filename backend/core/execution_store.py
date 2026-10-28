"""Persistence store interface and in-memory implementation for execution data."""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from schemas.execution import ExecutionRecord, AgentNode, ExecutionState, TimelineEntry
from observability.events import BaseEvent


class BaseExecutionStore(ABC):
    """Abstract base class for persisting executions, agent DAG nodes, and events."""

    @abstractmethod
    def create_execution(self, record: ExecutionRecord) -> None:
        """Saves a new execution record."""
        pass

    @abstractmethod
    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        """Retrieves an execution record by ID."""
        pass

    @abstractmethod
    def update_execution_status(self, execution_id: str, status: ExecutionState) -> Optional[ExecutionRecord]:
        """Updates the status of an execution record, updating updatedAt timestamp."""
        pass

    @abstractmethod
    def update_execution(self, record: ExecutionRecord) -> None:
        """Saves updates to an existing execution record."""
        pass

    @abstractmethod
    def list_executions(self) -> List[ExecutionRecord]:
        """Lists all execution records."""
        pass

    @abstractmethod
    def add_agent_node(self, execution_id: str, node: AgentNode) -> None:
        """Adds an agent node to the execution's DAG."""
        pass

    @abstractmethod
    def update_agent_node(self, execution_id: str, node: AgentNode) -> None:
        """Updates an existing agent node in the execution's DAG."""
        pass

    @abstractmethod
    def get_agent_nodes(self, execution_id: str) -> List[AgentNode]:
        """Retrieves all agent nodes for a given execution."""
        pass

    @abstractmethod
    def add_event(self, execution_id: str, event: Any) -> None:
        """Appends an event to the execution's event log."""
        pass

    @abstractmethod
    def get_events(self, execution_id: str) -> List[Any]:
        """Retrieves all events for a given execution."""
        pass

    @abstractmethod
    def append_timeline_entry(self, execution_id: str, entry: TimelineEntry) -> None:
        """Appends an entry to the execution's immutable timeline."""
        pass

    @abstractmethod
    def get_timeline(self, execution_id: str) -> List[TimelineEntry]:
        """Retrieves the full ordered timeline for a given execution."""
        pass


class InMemoryExecutionStore(BaseExecutionStore):
    """In-memory execution store for development."""

    def __init__(self):
        self._executions: Dict[str, ExecutionRecord] = {}
        self._agent_nodes: Dict[str, Dict[str, AgentNode]] = {}
        self._events: Dict[str, List[Any]] = {}
        self._timelines: Dict[str, List[TimelineEntry]] = {}

    def create_execution(self, record: ExecutionRecord) -> None:
        self._executions[record.id] = record
        self._agent_nodes[record.id] = {}
        self._events[record.id] = []
        self._timelines[record.id] = []

    def get_execution(self, execution_id: str) -> Optional[ExecutionRecord]:
        return self._executions.get(execution_id)

    def update_execution_status(self, execution_id: str, status: ExecutionState) -> Optional[ExecutionRecord]:
        record = self._executions.get(execution_id)
        if record:
            record.status = status
            record.updatedAt = time.time()
            if status == ExecutionState.RUNNING and not record.startedAt:
                record.startedAt = time.time()
            elif status in (ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.CANCELLED):
                record.completedAt = time.time()
                if record.startedAt:
                    record.totalLatency = int((record.completedAt - record.startedAt) * 1000)
            return record
        return None

    def update_execution(self, record: ExecutionRecord) -> None:
        if record.id in self._executions:
            record.updatedAt = time.time()
            self._executions[record.id] = record

    def list_executions(self) -> List[ExecutionRecord]:
        # Return sorted by creation time descending
        return sorted(self._executions.values(), key=lambda r: r.createdAt, reverse=True)

    def add_agent_node(self, execution_id: str, node: AgentNode) -> None:
        if execution_id not in self._agent_nodes:
            self._agent_nodes[execution_id] = {}
        self._agent_nodes[execution_id][node.id] = node

    def update_agent_node(self, execution_id: str, node: AgentNode) -> None:
        if execution_id in self._agent_nodes and node.id in self._agent_nodes[execution_id]:
            self._agent_nodes[execution_id][node.id] = node

    def get_agent_nodes(self, execution_id: str) -> List[AgentNode]:
        nodes_dict = self._agent_nodes.get(execution_id, {})
        return list(nodes_dict.values())

    def add_event(self, execution_id: str, event: Any) -> None:
        if execution_id not in self._events:
            self._events[execution_id] = []
        self._events[execution_id].append(event)

    def get_events(self, execution_id: str) -> List[Any]:
        return self._events.get(execution_id, [])

    def append_timeline_entry(self, execution_id: str, entry: TimelineEntry) -> None:
        if execution_id not in self._timelines:
            self._timelines[execution_id] = []
        self._timelines[execution_id].append(entry)
        # Keep the ExecutionRecord's embedded timeline in sync for API responses
        record = self._executions.get(execution_id)
        if record:
            record.timeline = self._timelines[execution_id][:]

    def get_timeline(self, execution_id: str) -> List[TimelineEntry]:
        return self._timelines.get(execution_id, [])


# Singleton instance
_store_instance = InMemoryExecutionStore()


def get_execution_store() -> BaseExecutionStore:
    return _store_instance
