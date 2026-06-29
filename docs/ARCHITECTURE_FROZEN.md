# Synapse v2.0 Architecture Freeze

Synapse v2.0 is feature-complete. The interfaces and contracts below are frozen for release stability and future compatibility.

## Frozen Contracts

### Specialist Interfaces
- Specialists implement the `BaseAgent` contract and return `AgentOutput`.
- Live specialists continue to use `LiveSpecialistOutput` for provider responses.
- Specialist registration order remains explicit in `SpecialistRegistry`.
- No release work may change specialist names, prompt-version wiring, or output schemas.

### Orchestrator Contract
- `Orchestrator.process_evidence()` accepts `list[Evidence]` and returns `ConsensusOutput`.
- Tick lifecycle remains: create tick, run agents, collect results, append blackboard, run consensus, finalize tick.
- Timeout handling and concurrency behavior are frozen.

### Replay Schema
- Replay artifacts remain centered on:
  - `events.json`
  - `metrics.json`
  - `manifest.json`
  - `prompt_bundle.json`
  - `replay_certificate.json`
- Supporting operational artifacts may be added around the replay, but the canonical replay schema is frozen.

### Event Schema
- Observability event models in `backend/observability/events.py` are frozen.
- Frontend demo event models in `backend/demo/events.py` are frozen.
- Release work must not add, remove, or rename fields in these schemas.

### PipelineState
- `PipelineState` remains the shared infrastructure state container for scenario execution.
- Its role in specialist progress tracking is frozen.

### Consensus Contract
- `ConsensusOutput` is frozen.
- Consensus behavior and weighting are frozen for this release.

### Provenance
- Manifest hashing, replay identifier derivation, and certificate validation are frozen.
- `ReplayValidator` remains the source of truth for provenance integrity.

### Evaluation Framework
- Golden dataset comparison flow, report generation, and benchmark methodology are frozen.
- Release work may improve packaging and reporting, but not the evaluation semantics.

### Operational Validator
- Validation stages, scoring, and deployment decision logic are frozen.
- Reporting may classify implementation and environmental status separately, but stage logic must remain unchanged.

## Allowed Future Changes
- Documentation
- Packaging and release workflow
- Repository hygiene
- Non-invasive reporting improvements

## Disallowed Future Changes Without A New Architecture Phase
- Specialist logic changes
- Orchestrator contract changes
- Replay schema changes
- Event schema changes
- Consensus changes
- Provenance changes
- New infrastructure abstractions
