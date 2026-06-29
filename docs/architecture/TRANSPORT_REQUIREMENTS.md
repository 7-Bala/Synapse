# Transport Requirements

This document defines the transport layer requirements necessary to bridge the existing Synapse backend with the Vite frontend. It evaluates requirements objectively before making a technology recommendation.

## 1. What Must Be Exposed
The transport layer must expose the following backend subsystems to the frontend:
- **Orchestrator Lifecycle**: Tick progression, execution status (idle, running, paused).
- **EventBus**: High-frequency telemetry events emitted by agents and validators.
- **Blackboard**: Shared memory state, including diffs per tick.
- **Agent Outputs**: Raw reasoning, confidence scores, token usage, and latency.
- **Tool Calls**: Exact JSON payloads and downstream responses.
- **Consensus & Validators**: Pass/fail states, blocked reasons, and committee logic.

## 2. Update Frequency
- **Telemetry & EventBus**: High-frequency (sub-second) during a live execution.
- **State Mutations (Blackboard)**: Emitted exactly once per orchestrator tick.
- **Static Retrieval (Replay)**: Instantaneous, loading historical execution state in bulk.

## 3. Request/Response Requirements
Traditional RPC operations required:
- Start new execution (with payload).
- Fetch historical execution (Replay Archive).
- Fetch golden datasets (Evaluation).
- Export Evidence / Reports.

## 4. Streaming Requirements
- **Live Execution Monitoring**: The frontend must receive push updates as agents reason and output tokens, rather than aggressively polling the backend.
- **EventBus Telemetry**: The UI must consume the synchronous `EventBus` firehose without dropping events.

## 5. Bidirectional Requirements
The transport layer must support asynchronous commands sent from the client while a streaming execution is active:
- **Pause/Resume**: Sending control signals to halt the `Orchestrator`.
- **Validator Overrides**: The engineer explicitly approves a blocked tool call mid-execution.
- **Inject Context**: The engineer modifies the Blackboard memory while the orchestrator is paused.

## 6. Latency Requirements
- **UI Responsiveness**: The IDE must feel instantaneous (< 50ms) when switching nodes or scrubbing replay ticks locally.
- **Backend Sync**: Telemetry latency from backend to frontend should be < 100ms to maintain the illusion of a live debugger.

## 7. Transport Options Evaluated
1. **REST + Polling**
   - *Pros*: Simple, native to standard web servers.
   - *Cons*: High latency, high overhead for frequent state updates, cannot cleanly handle bidirectional interrupts mid-tick.
2. **REST + Server-Sent Events (SSE)**
   - *Pros*: Solves the streaming requirement natively over HTTP.
   - *Cons*: Unidirectional. Requires separate REST endpoints for bidirectional commands (Pause/Override), leading to race conditions between the SSE stream and REST mutations.
3. **gRPC-Web**
   - *Pros*: Strongly typed, performant.
   - *Cons*: Heavy infrastructure requirement, complex setup for a local Python-to-Vite IDE architecture.
4. **WebSockets**
   - *Pros*: Fully bidirectional, persistent connection, extremely low latency. Handles the `EventBus` firehose and bidirectional override commands cleanly over a single multiplexed channel.

## 8. Recommendation
**WebSockets** (with a fallback to standard REST for bulk retrieval). 
Because Synapse acts as an interactive debugger, the requirement to *pause execution, inject context, and override validators* mid-flight necessitates a persistent, bidirectional connection to the backend `Orchestrator` and `EventBus`.
