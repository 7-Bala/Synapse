# State Ownership

This document defines the strict, non-duplicated ownership of every piece of state in the Synapse architecture. 
To prevent desync and race conditions, state must never be duplicated across layers. The frontend is merely a projection of the backend state, with the exception of local UI configurations.

## Core State Objects

### 1. Execution
- **Owner**: `Orchestrator` (Backend)
- **Cache?**: No
- **Persistent?**: No (during run), Yes (after completion via Replay Archive)
- **Frontend/Backend**: Backend
- **Mutable/Immutable**: Mutable (by Orchestrator only)

### 2. Blackboard
- **Owner**: `Blackboard` (Backend)
- **Cache?**: No
- **Persistent?**: Yes (Snapshots per tick)
- **Frontend/Backend**: Backend
- **Mutable/Immutable**: Append-only (Immutable history, mutable `HEAD`)

### 3. Consensus
- **Owner**: `Consensus Engine` (Backend)
- **Cache?**: No
- **Persistent?**: Yes (recorded in tick context)
- **Frontend/Backend**: Backend
- **Mutable/Immutable**: Immutable once reached

### 4. Validator Result
- **Owner**: `OperationalValidator` / Agents (Backend)
- **Cache?**: No
- **Persistent?**: Yes (Logged in EventBus/Replay)
- **Frontend/Backend**: Backend
- **Mutable/Immutable**: Immutable (Overrides create a *new* result event, they do not mutate the old one)

### 5. Replay Archive
- **Owner**: `ArtifactWriter` / Storage (Backend)
- **Cache?**: Yes (Frontend caches historical ticks for smooth scrubbing)
- **Persistent?**: Yes
- **Frontend/Backend**: Backend (Source of Truth)
- **Mutable/Immutable**: Strictly Immutable

### 6. Selected Node
- **Owner**: `useExecutionStore` (Frontend)
- **Cache?**: Local memory
- **Persistent?**: No (lost on refresh)
- **Frontend/Backend**: Frontend
- **Mutable/Immutable**: Mutable

### 7. Replay Cursor (Temporal Tick)
- **Owner**: `useExecutionStore` (Frontend)
- **Cache?**: Local memory
- **Persistent?**: No
- **Frontend/Backend**: Frontend
- **Mutable/Immutable**: Mutable

### 8. UI Layout Configuration (Dock Sizes, Panel Visibility)
- **Owner**: `useAppStore` (Frontend)
- **Cache?**: `localStorage` (Frontend)
- **Persistent?**: Yes (Local to browser)
- **Frontend/Backend**: Frontend
- **Mutable/Immutable**: Mutable

---

## State Flow Principles
1. **The Backend Owns The Truth**: The frontend never calculates consensus, validation passes, or state diffs. It only renders what the backend provides.
2. **Commands vs. State**: The frontend sends *commands* (e.g., `StartExecution`, `OverrideValidator`). The backend processes the command and mutates the state. The backend then emits an *event*. The frontend updates its projection based on the event.
3. **No Optimistic Updates for High-Stakes Actions**: When overriding a validator, the frontend must not instantly mark the node as green. It must wait for the backend `ValidatorOverridden` event to ensure the override was actually accepted.
