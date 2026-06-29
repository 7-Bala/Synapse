# Existing System Trace

This document maps the existing Synapse backend architecture and its execution lifecycle. The goal is to discover and reuse the existing backend rather than inventing a new one.

## 1. Current Backend Architecture

### Key Subsystems
- **Orchestrator** (`backend/core/orchestrator.py`, `Orchestrator` class)
  - **Responsibility**: Manages the execution lifecycle for the backend, processing evidence, running agents, collecting results, appending to the Blackboard, and running Consensus.
  - **Public Methods**: `process_evidence()`
  - **Inputs**: `List[Evidence]`
  - **Outputs**: `ConsensusOutput`
  - **Dependencies**: `BaseAgent`, `Blackboard`, `TickContext`

- **Blackboard** (`backend/core/blackboard.py`, `Blackboard` class)
  - **Responsibility**: An append-only shared memory space for storing agent outputs.
  - **Public Methods**: `append()`, `get_all()`, `get_current_state()`, `snapshot()`, `latest_tick()`, `entries_for_tick()`, `latest_entry()`
  - **Data Models**: `BlackboardEntry`

- **Tick Context** (`backend/core/tick_context.py`, `TickContext` class)
  - **Responsibility**: Immutable context passed to agents during a specific tick.
  - **Data Models**: `TickContext`

- **Consensus** (`backend/core/consensus.py`)
  - **Responsibility**: Runs consensus logic to determine the final decision from a list of agent outputs.
  - **Outputs**: `ConsensusOutput`

- **Event Bus** (`backend/observability/event_bus.py`, `EventBus` class)
  - **Responsibility**: A lightweight, synchronous event bus for observability telemetry.
  - **Public Methods**: `subscribe()`, `emit()`
  - **Data Models**: `BaseEvent`

- **Operational Validator** (`backend/validators/operational_validator.py`, `OperationalValidator`)
  - **Responsibility**: The authoritative deployment readiness gate for Synapse. Evaluates readiness using a 10-stage pipeline without mutating state.
  - **Current Entrypoints**: CLI with `--json / --summary / --strict / --fail-fast` flags.

## 2. Current Execution Lifecycle

Trace of one execution through the current backend:

1. **User Input / Entry Function**: (Currently driven by `backend/demo/events.py` or `backend/demo/recorder.py` simulating downstream events).
2. **Orchestrator**: `Orchestrator.process_evidence(new_evidence)` is called.
3. **Tick Creation**: A new `TickContext` is created with the evidence delta and a snapshot of the blackboard.
4. **Specialists (Agents)**: `Orchestrator._run_agents()` executes all registered agents concurrently.
5. **Results Collection**: `Orchestrator._collect_results()` filters valid `AgentOutput`s.
6. **Blackboard**: `Orchestrator._append_blackboard()` appends outputs to the `Blackboard`.
7. **Consensus**: `Orchestrator._run_consensus()` synthesizes the agent outputs into a `ConsensusOutput`.
8. **Final Output**: The tick finalizes and returns the `ConsensusOutput`.

## 3. Current Data Models

- **TickContext** (`backend/core/tick_context.py`):
  - **Owner**: Orchestrator
  - **Lifecycle**: Created per tick, immutable.
- **AgentOutput** (`backend/schemas/agent.py`):
  - **Owner**: Specialist Agents
  - **Producer**: Agents during a tick
  - **Consumer**: Orchestrator, Consensus, Blackboard
- **LiveSpecialistOutput** (`backend/schemas/agent.py`):
  - **Owner**: Live Agents
  - **Details**: Contains `finding`, `reasoning`, `latency_ms`, `tokens_in`, `tokens_out`, `citations`.
- **Evidence** (`backend/schemas/evidence.py`):
  - **Owner**: Event sources / Downstream systems
  - **Consumer**: Orchestrator / Agents
- **BlackboardEntry** (`backend/schemas/blackboard.py`):
  - **Owner**: Blackboard
  - **Lifecycle**: Appended immutably during a tick.
- **ConsensusOutput** (`backend/schemas/consensus.py`):
  - **Owner**: Consensus Engine
  - **Producer**: `run_minimal_consensus`
- **ValidationFinding** / **StageResult** (`backend/validators/operational_validator.py`):
  - **Owner**: Operational Validator

## 4. Current Transport Layer

- **Is there already an HTTP layer?** No. There is no FastAPI, Flask, or Django app in `backend/api/app.py` (it is an empty file).
- **Is there already an event bus?** Yes. `backend/observability/event_bus.py` implements a synchronous, in-memory event bus.
- **Is there already a CLI entrypoint?** Yes. Scripts in `backend/demo/` and CLI arguments in `operational_validator.py` serve as the current entrypoints. 
- **Is there already an execution lifecycle?** Yes. Handled synchronously by `Orchestrator.process_evidence()`.

## 5. Current Frontend Mapping

Current frontend pages and their relation to the backend:

- **DashboardPage.tsx (ExecutionWorkspace)**
  - **Current Store**: None (mocked state).
  - **Current API**: None.
  - **Current Backend Class**: Orchestrator / EventBus
  - **Status**: Placeholder/Mocked.
- **Sidebar.tsx (WorkspaceDock)**
  - **Current Store**: `useAppStore` (Frontend only state).
  - **Status**: Implemented for UI routing, disconnected from backend.

## 6. Missing Integration Points

- **API/Transport**: The Python backend operates strictly in-memory (EventBus, Orchestrator) or via CLI scripts (`demo/recorder.py`). There is currently no transport layer (e.g., WebSocket or HTTP REST) to bridge the Python memory space to the React/Vite frontend.
- **State Hydration**: The frontend has no mechanism to subscribe to the `EventBus` or poll the `Orchestrator` state.

## 7. Minimal Implementation Required

To bridge the frontend and backend without replacing the existing architecture, the minimal implementation is:
1. **Transport Layer**: Wrap the existing `Orchestrator` and `EventBus` in a lightweight local server (e.g., standard HTTP or WebSocket) in `backend/api/app.py` strictly for state exposure, not business logic.
2. **Frontend Store**: Create a Zustand store that listens to this transport layer.
3. **Execution Inspector UI**: Map the incoming `LiveSpecialistOutput` and `BlackboardEntry` objects directly to the nodes in the Execution Graph.
