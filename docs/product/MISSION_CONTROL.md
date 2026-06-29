# Mission Control Specification

## Purpose
The definitive global view of the Synapse platform. It provides immediate answers to: Is the system healthy? What swarms are running? Are there any blocked workflows requiring human intervention?

## User Story
As a Platform Operator, when I log in at 9 AM, I need to instantly see if any autonomous swarms failed overnight or are currently blocked pending approval, so that I can unblock production workflows before they impact users.

## Layout
```text
=============================================================================
[Workspace Header] Breadcrumbs | Global Search | Environment | User Profile
=============================================================================
[Dock]      | [Operations Rail]                                             |
- Execute   | - Quick Actions (Deploy, Stop All)                            |
- Invest    | - Active Swarms List                                          |
- Analyze   | - Blocked Alerts (Requires Human)                             |
- Operate   |---------------------------------------------------------------|
- Docs      | [Command Canvas]                                              |
            | - Global Topology Heatmap (Visualizing active nodes)          |
            | - Live Event Stream (Terminal-like scrolling logs)            |
            |---------------------------------------------------------------|
            | [Intelligence Rail]                                           |
            | - AI System Insights (e.g. "Consensus rate dropped 4%")       |
            | - Token Spend Velocity                                        |
=============================================================================
[Bottom Utilities] System Status (Green) | Latency | Version | Connection
=============================================================================
```

## Panel Specifications

### 1. Operations Rail: Active Swarms
- **Purpose:** Show running workloads.
- **Inputs:** Stream of active `orchestrator_sessions`.
- **Outputs:** List of cards (Swarm ID, Status, Uptime).
- **Update Frequency:** 1000ms via WebSocket.
- **Interactions:** Click to navigate to `/execute/{id}`.
- **Empty State:** "No active swarms. Deploy a workload to begin."
- **Loading State:** Skeleton stack.
- **Failure State:** "Failed to sync active sessions." with Retry button.

### 2. Command Canvas: Global Topology Heatmap
- **Purpose:** Spatial representation of system load across agent pools.
- **Inputs:** Aggregated metrics per agent role.
- **Outputs:** Honeycomb or Node-graph heatmap.
- **Update Frequency:** 5000ms.
- **Hover:** Displays node health, active count, queue depth.

### 3. Intelligence Rail: Token Spend Velocity
- **Purpose:** Prevent runaway API costs from infinite agent loops.
- **Inputs:** LLM usage metrics.
- **Outputs:** Sparkline chart showing tokens/sec over the last 1 hour.
- **Update Frequency:** 10000ms.
- **Failure State:** Render empty sparkline with warning icon.
