# Backend → UI Mapping

Every backend capability must have a frontend consumer.

## Orchestrator
- **Backend:** Manages state transitions, workflow DAGs, agent lifecycles.
- **Consumer:** `Execute Workspace`
- **UI Element:** `Topology Canvas` (Visual DAG), `Execution Nodes` (Agents).

## Replay
- **Backend:** Time-travel debugging, deterministic state reconstruction.
- **Consumer:** `Investigate Workspace`
- **UI Element:** `TimelineTrace`, `Replay Scrub Bar`.

## Consensus
- **Backend:** Multi-agent voting, disagreement resolution.
- **Consumer:** `Analyze Workspace`
- **UI Element:** `Consensus Breakdown Matrix`, `Agreement Confidence Score`.

## Evaluation & Benchmarks
- **Backend:** Running swarms against static datasets, scoring.
- **Consumer:** `Analyze Workspace`
- **UI Element:** `Benchmark Compare Table`, `Radar Chart`.

## Blackboard
- **Backend:** Shared memory space for swarms.
- **Consumer:** `Execute Workspace` & `Investigate Workspace`
- **UI Element:** `Memory Inspector Panel`, `JSON State Diff Viewer`.

## Health & Infrastructure
- **Backend:** Node health, API quotas, latency.
- **Consumer:** `Operate Workspace` & `Mission Control`
- **UI Element:** `System Status Indicator`, `Token Velocity Chart`.

## Validators
- **Backend:** Semantic checks, safety rails, output parsing validation.
- **Consumer:** `Execute Workspace`
- **UI Element:** `Guardrail Alert Toast`, `Validator Log Node`.
