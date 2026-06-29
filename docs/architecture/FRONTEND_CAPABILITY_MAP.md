---
Version: 1.0
Generated Date: 2026-06-29
Repository Commit: Current HEAD
Owner: Synapse UI Refactor Team
Status: Active
Last Verified: 2026-06-29
---

# Frontend Capability Map
| Workspace | Purpose | Components | Stores |
|---|---|---|---|
| Mission Control | High-level system overview | SystemHealth, LiveEventFeed | useHealthStore |
| Execute | Pipeline topology & live orchestrator | TopologyCanvas, ExecutionNode | useOrchestratorStore |
| Investigate | Replay engine & state diffs | TickTimeline, StateDiffViewer | useReplayStore |
| Operate | Validator monitoring | ValidatorTerminal | useOpsStore |
