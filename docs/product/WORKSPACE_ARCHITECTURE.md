# Workspace Architecture

## Mission Control
- **Purpose:** The global command center. High-level situational awareness across all swarms.
- **User Persona:** MLOps, Platform Lead.
- **Entry Point:** `/` (Default Route)
- **Primary Task:** Assess global system health and active swarm count.
- **Secondary Tasks:** Identify anomalies, view recent critical alerts.
- **Backend Modules:** Health, Orchestrator (Summary).
- **Required APIs:** `/api/v1/health`, `/api/v1/swarms/active`
- **Required Visualizations:** Global Swarm Heatmap, Real-time Event Feed.
- **Required Panels:** System Status, Active Topologies, Anomaly Radar.

## Execute
- **Purpose:** Live orchestration and intervention of active agent workflows.
- **User Persona:** AI Engineer, Operator.
- **Entry Point:** `/execute`
- **Primary Task:** Watch a swarm execute in real-time, intervene if necessary.
- **Required Backend Modules:** Orchestrator, Validators.
- **Required Visualizations:** Interactive Topology Canvas.
- **Required Panels:** Topology View, Node Inspector, Active Memory (Blackboard), Tool Execution Feed.
- **Actions:** Pause, Resume, Inject Message, Approve Tool Call.

## Investigate
- **Purpose:** Post-mortem debugging and deterministic replay of past executions.
- **User Persona:** AI Engineer.
- **Entry Point:** `/investigate`
- **Primary Task:** Find out *why* a specific run failed or hallucinated.
- **Required Backend Modules:** Replay, Blackboard.
- **Required Visualizations:** Timeline/Waterfall Trace, Diff Viewer.
- **Required Panels:** Execution Selection, Timeline Trace, State Diff (Before/After), Token/Latency breakdown.

## Analyze
- **Purpose:** Quantitative evaluation of models and swarm configurations over time.
- **User Persona:** Data Scientist, AI Engineer.
- **Entry Point:** `/analyze`
- **Primary Task:** Compare Swarm V1 vs Swarm V2 against a benchmark dataset.
- **Required Backend Modules:** Evaluation, Benchmarks, Consensus.
- **Required Visualizations:** Distribution Curves, Confusion Matrices, Radar Charts.
- **Required Panels:** Benchmark Selector, Metric Comparison, Consensus Analysis.

## Operate
- **Purpose:** Infrastructure management, cluster health, API key rotation, system config.
- **User Persona:** MLOps, DevOps.
- **Entry Point:** `/operate`
- **Primary Task:** Manage compute resources and API rate limits.
- **Required Backend Modules:** Health, Infrastructure.
- **Required Panels:** Resource Usage, Key Management, Rate Limiters.

## Documentation
- **Purpose:** Internal engineering specifications and Design System showcase.
- **User Persona:** Frontend Engineer, Platform Engineer.
- **Entry Point:** `/design-system`
- **Primary Task:** Reference UI primitives and token definitions.
