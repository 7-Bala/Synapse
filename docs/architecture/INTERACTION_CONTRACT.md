# Interaction Contract

This document maps the strict flow of interaction for every professional workflow in the Synapse IDE. It defines the path from User Action → Frontend → Transport → Backend → Frontend Feedback.

## Minimum Workflows

### 1. Start Execution
- **User Action**: User submits a payload via the Command Palette.
- **Frontend Component**: `CommandPalette`
- **Store Action**: `executionStore.startExecution(payload)`
- **Transport**: `WebSocket: emit("START_EXECUTION")`
- **Backend Class**: `Orchestrator`
- **Backend Method**: `process_evidence(payload)`
- **Backend Event**: `ExecutionStarted`
- **Frontend Update**: `executionStore` receives event, sets status to `running`.
- **User Feedback**: Workspace transitions to Execution Graph; graph begins rendering root nodes.

### 2. Pause Execution
- **User Action**: User clicks the "Pause" button in the Workspace Header.
- **Frontend Component**: `WorkspaceHeader`
- **Store Action**: `executionStore.pauseExecution()`
- **Transport**: `WebSocket: emit("PAUSE_EXECUTION")`
- **Backend Class**: `Orchestrator`
- **Backend Method**: `pause()`
- **Backend Event**: `ExecutionPaused`
- **Frontend Update**: `executionStore` sets status to `paused`.
- **User Feedback**: UI indicators turn yellow; active nodes pulse indicates suspended state.

### 3. Resume Execution
- **User Action**: User clicks the "Resume" button.
- **Frontend Component**: `WorkspaceHeader`
- **Store Action**: `executionStore.resumeExecution()`
- **Transport**: `WebSocket: emit("RESUME_EXECUTION")`
- **Backend Class**: `Orchestrator`
- **Backend Method**: `resume()`
- **Backend Event**: `ExecutionResumed`
- **Frontend Update**: `executionStore` sets status to `running`.
- **User Feedback**: Paused indicators resolve; graph resumes live updates.

### 4. Select Node
- **User Action**: User clicks a Node in the Execution Graph.
- **Frontend Component**: `ExecutionGraph`
- **Store Action**: `executionStore.selectNode(nodeId)`
- **Transport**: *Local Only* (Data already synced via EventBus).
- **Backend Class**: N/A
- **Backend Method**: N/A
- **Backend Event**: N/A
- **Frontend Update**: `executionStore` updates `selectedNodeId`.
- **User Feedback**: `ExecutionInspector` opens and populates with node's raw reasoning and prompt.

### 5. Replay Tick
- **User Action**: User drags the Timeline scrubber.
- **Frontend Component**: `ReplayTimeline`
- **Store Action**: `executionStore.setReplayTick(tickId)`
- **Transport**: *Local Only* (If history is cached) OR `REST: GET /api/v1/replay/{id}/ticks/{tickId}`
- **Backend Class**: `ReplayEngine`
- **Backend Method**: `get_state_at_tick(tickId)`
- **Backend Event**: N/A
- **Frontend Update**: `executionStore` overwrites current graph and blackboard state with historical snapshot.
- **User Feedback**: The entire workspace visually reverts to the exact state at that temporal tick.

### 6. Open Blackboard
- **User Action**: User clicks the Blackboard toggle in the Dock.
- **Frontend Component**: `WorkspaceDock`
- **Store Action**: `uiStore.togglePanel('blackboard')`
- **Transport**: N/A
- **Backend Class**: `Blackboard`
- **Backend Method**: N/A
- **Backend Event**: `BlackboardUpdated` (Continuously streamed)
- **Frontend Update**: Panel renders latest synced state.
- **User Feedback**: The Blackboard Explorer panel opens, showing live memory JSON.

### 7. Inspect Consensus
- **User Action**: User clicks a Consensus node in the Graph.
- **Frontend Component**: `ExecutionGraph`
- **Store Action**: `executionStore.selectNode(consensusNodeId)`
- **Transport**: N/A
- **Backend Class**: `Consensus`
- **Backend Method**: `run_minimal_consensus()`
- **Backend Event**: `ConsensusReached`
- **Frontend Update**: `ConsensusExplorer` renders agent outputs and differences.
- **User Feedback**: Screen displays a visual diff of Agent A, Agent B, Agent C and the final resolution.

### 8. Inspect Validator
- **User Action**: User clicks a blocked Validator node.
- **Frontend Component**: `ExecutionGraph`
- **Store Action**: `executionStore.selectNode(validatorNodeId)`
- **Transport**: N/A
- **Backend Class**: `OperationalValidator`
- **Backend Method**: N/A
- **Backend Event**: `ValidationFailed`
- **Frontend Update**: `ValidatorConsole` renders failure reason.
- **User Feedback**: Inspector displays the exact constraint violated and the offending payload.

### 9. Inspect Evidence
- **User Action**: User clicks an Evidence badge in the Inspector.
- **Frontend Component**: `ExecutionInspector`
- **Store Action**: `evidenceStore.viewEvidence(evidenceId)`
- **Transport**: `REST: GET /api/v1/evidence/{evidenceId}`
- **Backend Class**: `Evidence`
- **Backend Method**: `get_evidence()`
- **Backend Event**: N/A
- **Frontend Update**: `EvidenceBrowser` modal/panel opens.
- **User Feedback**: Engineer sees the raw retrieved data block.

### 10. View Tool Call
- **User Action**: User clicks a Tool Call entry inside the Inspector.
- **Frontend Component**: `ToolCallExplorer`
- **Store Action**: N/A
- **Transport**: N/A
- **Backend Class**: `SpecialistAgent`
- **Backend Method**: N/A
- **Backend Event**: `ToolCallExecuted`
- **Frontend Update**: Expands tool accordion.
- **User Feedback**: Displays the raw JSON payload sent to the external API and its response.

### 11. Search Execution
- **User Action**: User presses `Cmd+K` and types a query.
- **Frontend Component**: `CommandPalette`
- **Store Action**: N/A
- **Transport**: `REST: GET /api/v1/executions/search?q={query}`
- **Backend Class**: `SearchIndex` / `ReplayArchive`
- **Backend Method**: `search_history()`
- **Backend Event**: N/A
- **Frontend Update**: Populates search results list.
- **User Feedback**: Displays matching executions or specific historical ticks.

### 12. Override Validator
- **User Action**: User clicks "Override & Proceed" on a blocked Validator node.
- **Frontend Component**: `ValidatorConsole`
- **Store Action**: `executionStore.overrideValidator(nodeId)`
- **Transport**: `WebSocket: emit("OVERRIDE_VALIDATOR", { nodeId })`
- **Backend Class**: `Orchestrator`
- **Backend Method**: `force_proceed(nodeId)`
- **Backend Event**: `ValidatorOverridden`
- **Frontend Update**: `executionStore` clears blocked status.
- **User Feedback**: Node turns from red to green; execution graph resumes progression.

### 13. Inject Context
- **User Action**: User edits a JSON value in the Blackboard Explorer and saves.
- **Frontend Component**: `BlackboardExplorer`
- **Store Action**: `executionStore.mutateBlackboard(path, value)`
- **Transport**: `WebSocket: emit("MUTATE_BLACKBOARD", { path, value })`
- **Backend Class**: `Blackboard`
- **Backend Method**: `append()` (manual injection entry)
- **Backend Event**: `BlackboardUpdated`
- **Frontend Update**: Local store confirms mutation.
- **User Feedback**: The Blackboard flashes green indicating a manual override was committed to state.

### 14. Export Evidence
- **User Action**: User clicks "Export JSON" on the Evidence panel.
- **Frontend Component**: `EvidenceBrowser`
- **Store Action**: N/A
- **Transport**: `REST: GET /api/v1/evidence/{id}/export`
- **Backend Class**: `ArtifactWriter`
- **Backend Method**: N/A
- **Backend Event**: N/A
- **Frontend Update**: Browser triggers file download.
- **User Feedback**: A `.json` file downloads to the user's machine.
