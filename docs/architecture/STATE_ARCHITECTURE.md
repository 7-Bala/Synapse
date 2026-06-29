---
Version: 1.0
Generated Date: 2026-06-29
Repository Commit: Current HEAD
Owner: Synapse UI Refactor Team
Status: Active
Last Verified: 2026-06-29
---

# State Architecture (Zustand)
- `useWorkspaceStore`: Frontend-owned. Manages panel layouts and persistent UI context.
- `useOrchestratorStore`: Backend-owned. Hydrated via WebSocket. No duplicate state.
- `useReplayStore`: Backend-owned. Forensic timeline bounds.
