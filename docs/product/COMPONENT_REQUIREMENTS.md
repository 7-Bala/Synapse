# Future Component Requirements

Instead of building generic components without context, all future components must adhere to these specifications.

## 1. ExecutionNode (Visualization)
- **Purpose:** Represents a single autonomous agent on the Topology Canvas.
- **Consumers:** `Execute Workspace`, `Investigate Workspace`.
- **Props:** `id`, `status` (idle, running, blocked, complete, failed), `agentName`, `latency`, `tokenUsage`.
- **Interactions:** Click -> Opens Inspector. Hover -> Shows quick stats tooltips.
- **States:** Pulsing border when running. Amber pulse when blocked.
- **Backend Dependency:** `Orchestrator Node State`.

## 2. TokenMetricBadge (Data Display)
- **Purpose:** Dense inline display of token usage and associated cost.
- **Consumers:** `Inspector`, `Intelligence Rail`.
- **Props:** `promptTokens`, `completionTokens`, `modelTier`.
- **Formatting:** Must use `formatBytes` and `formatNumber` from `utils/formatters.ts`.

## 3. BlackboardDiffViewer (Data Display)
- **Purpose:** Shows what changed in the shared memory state between two execution steps.
- **Consumers:** `Investigate Workspace`.
- **Props:** `previousState` (JSON), `newState` (JSON).
- **Backend Dependency:** `Blackboard Replay API`.
