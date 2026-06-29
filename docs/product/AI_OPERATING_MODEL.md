# Synapse: AI Operating Model

This document establishes the highest-level operational specification for Synapse. It serves as the foundational operating model from which every workspace, API, and UI component must derive. Synapse is an AI Operating System / IDE, not a monitoring dashboard.

---

## 1. The AI Execution Lifecycle

The UI must emerge naturally from the execution lifecycle. Every execution transitions through the following core stages:

1. **Idle**
   - **Purpose**: System is ready to accept workloads.
   - **Backend Owner**: Orchestrator.
   - **Interactions**: Engineer configures and initiates a new execution or selects a past execution.

2. **Execution Requested**
   - **Purpose**: A payload (goal/prompt) is submitted to the system.
   - **Produced Artifacts**: Execution ID, Initial Blackboard State.

3. **Planner & Task Decomposition**
   - **Purpose**: The Planner agent breaks the user goal into a DAG of specialized tasks.
   - **Backend Owner**: Planner Agent.
   - **Produced Artifacts**: Execution Graph (Nodes and Edges).
   - **Failure Modes**: Unsolvable goal, cyclic dependency in tasks.

4. **Specialist Assignment & Reasoning**
   - **Purpose**: Individual agents (Specialists) are assigned to nodes and begin LLM reasoning.
   - **Backend Owner**: Specialist Agents.
   - **Produced Artifacts**: Prompt assemblies, raw reasoning (Chain of Thought), tokens consumed.
   - **Interactions**: Engineer inspects raw reasoning in real-time.

5. **Tool Calls & Evidence Collection**
   - **Purpose**: Specialists interact with the external world to gather data or execute actions.
   - **Backend Owner**: Tool Execution Engine.
   - **Produced Artifacts**: Tool payload (JSON), raw responses, Evidence items.
   - **Failure Modes**: API timeouts, schema mismatches, unauthorized actions.
   - **Interactions**: Engineer traces specific tool executions or manually overrides blocked tools.

6. **Validation**
   - **Purpose**: Validators check the specialist's proposed actions against security, logic, and schema constraints before they mutate global state.
   - **Backend Owner**: Validation Engine.
   - **Emitted Events**: Pass/Fail, Blocked.
   - **Interactions**: Engineer inspects failure reasons and provides manual override if blocked.

7. **Consensus**
   - **Purpose**: For high-stakes decisions, a committee of agents votes on the outcome.
   - **Backend Owner**: Consensus Engine.
   - **Produced Artifacts**: Agreements, disagreements, final resolution.
   - **Interactions**: Engineer reviews dissenting opinions and the synthesis process.

8. **Blackboard Commit (Memory Updates)**
   - **Purpose**: Approved knowledge and state mutations are written to the shared Blackboard.
   - **Backend Owner**: Blackboard / Memory Manager.
   - **Produced Artifacts**: Blackboard Diffs, provenance linking back to Evidence.

9. **Final Output & Evaluation**
   - **Purpose**: The orchestration completes and generates the final deliverable.
   - **Backend Owner**: Orchestrator / Evaluation Engine.
   - **Interactions**: Engineer benchmarks the run against golden datasets.

10. **Replay Archive (Completed)**
    - **Purpose**: The execution is frozen into an immutable timeline for future auditing.
    - **Backend Owner**: Replay Engine / Storage.

---

## 2. User Personas

Synapse serves distinct engineering personas, each utilizing different primary work surfaces:

1. **AI Engineer**
   - **Responsibilities**: Prompt engineering, agent chaining, tool development.
   - **Daily Workflows**: Debugging why a specialist hallucinated, testing new prompts.
   - **Primary Work Surfaces**: Execution Inspector, Prompt Inspector, Replay Timeline.

2. **ML Researcher**
   - **Responsibilities**: Model evaluation, output quality, consensus behavior.
   - **Daily Workflows**: Comparing models across identical executions.
   - **Primary Work Surfaces**: Evaluation Lab, Consensus Explorer.

3. **Platform Engineer / Operations Engineer**
   - **Responsibilities**: System stability, latency, orchestrator health, token costs.
   - **Daily Workflows**: Tracing tool call latency, analyzing token spend velocity.
   - **Primary Work Surfaces**: Execution Graph, Tool Call Explorer.

4. **Security Engineer**
   - **Responsibilities**: Validating safe execution, auditing blocked tool calls.
   - **Daily Workflows**: Reviewing blocked actions, overriding false positives.
   - **Primary Work Surfaces**: Validator Console, Evidence Browser.

---

## 3. Operational Modes

The UI contextually shifts based on the operational mode:

1. **Live Execution Mode**
   - The UI streams events in real-time. The Execution Graph builds out dynamically. The timeline is locked to `HEAD`.
2. **Replay Mode**
   - The UI is frozen in time. The Replay Scrubber controls the entire IDE. Engineers can step through ticks backward and forward.
3. **Intervention Mode**
   - Execution is paused. The engineer edits the Blackboard directly, alters a prompt, or forces a Validator override.
4. **Evaluation Mode**
   - Split-screen comparison of multiple executions or runs against benchmark data.

---

## 4. Object Hierarchy

First-class objects in Synapse and their primary actions:

- **Execution**: Owns the entire run. (Actions: Pause, Resume, Replay, Fork)
- **Agent (Planner/Specialist)**: Executes logic. (Actions: Inspect Prompt, Inspect Reasoning)
- **Node**: A step in the Execution Graph. (Actions: Inspect, Replay Node)
- **Tool Call**: External integration. (Actions: Inspect Payload, Retry)
- **Evidence**: Raw data collected. (Actions: Trace Provenance, Export)
- **Validator**: Security/Logic gate. (Actions: Override, Inspect Rule)
- **Consensus**: Multi-agent agreement. (Actions: View Dissent, Expand Voting)
- **Blackboard Entry**: Shared memory state. (Actions: Diff, Edit, Trace Producer)

---

## 5. Navigation Mental Model

Navigation strictly mirrors how an engineer investigates an AI system (drill-down hierarchy). It does not use generic dashboard sections.

```text
Execution (The root context)
├── Execution Graph (Topology of the run)
├── Agents / Nodes (Execution Inspector)
├── Blackboard (Shared memory state)
├── Tool Calls (External interactions)
├── Evidence (Raw data)
├── Validators (Security & constraints)
├── Consensus (Agreement workflows)
└── Replay (Temporal scrubbing)
```

---

## 6. Interaction Grammar

Every object across all workspaces must adhere to a shared interaction vocabulary:
- **Inspect**: Open the deepest level of detail (e.g., raw JSON or raw Prompt).
- **Replay**: Jump the temporal scrubber to the exact tick this object was created/mutated.
- **Diff**: Compare state A to state B (critical for Blackboard and Prompts).
- **Override**: Force a system constraint to pass (used in Validators).
- **Trace / Follow**: Navigate from an output back to the Evidence that produced it (Provenance).
- **Pause / Resume**: Control the orchestrator execution.

---

## 7. Cross-Workspace Synchronization

The **Execution** is a global singleton state for the IDE.
If an engineer selects "Execution #128", *every* workspace (Blackboard, Inspector, Graph, Tool Calls) instantly mounts Execution #128.
Furthermore, the **Replay Scrubber** acts as a global temporal lock. If the engineer scrubs to "Tick 14", the entire UI reverts to its exact state at Tick 14. No workspace ever becomes temporally or contextually isolated.

---

## 8. Information Density (Progressive Disclosure)

The UI must progressively reveal complexity to support long, professional sessions without overwhelming the engineer.

- **Zoomed Out (Fleet Level)**: High-level list of Executions, active status, and aggregate alerts.
- **Zoomed In (Execution Level)**: The Execution Graph, active Nodes, and summary of Blackboard mutations.
- **Maximum Zoom (Inspector Level)**: Raw prompts, raw JSON tool payloads, full stack traces, and literal LLM string outputs.
