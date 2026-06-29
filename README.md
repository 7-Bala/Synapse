# Synapse

**Synapse** is an AI Operating System designed as an advanced execution environment and debugger for deterministic multi-agent runtimes. It is not an enterprise dashboard; it is an integrated engineering environment (IDE) built to track, inspect, and trace AI execution lifecycles in real time.

## Project Overview

Synapse provides deep observability into the reasoning, evidence collection, and consensus loops of AI agents. Rather than presenting static metrics, it acts as a transparent window into exactly what an AI agent is doing, why it's doing it, and what state led to its decisions.

## Features

- **Execution Telemetry Engine**: Zero-overhead telemetry emitted via an asynchronous EventBus.
- **Mission Control Workspace**: A high-fidelity, deterministic frontend that reflects the real-time state of the backend.
- **Evidence Lifecycle Tracking**: Real-time rendering of evidence collection, resolution, and validation.
- **Agent Tracing**: Pinpoint latency, errors, and reasoning loops at the specialist level.
- **Decoupled Architecture**: Strict separation of concerns between backend orchestration, transport layer, and frontend stores.

## Architecture Overview

Synapse enforces strict layer separation:

1. **Backend Orchestrator**: Manages execution state, ticks, and agent invocation.
2. **Observability Layer**: Hooks into Orchestrator callbacks to translate lifecycle state into canonical events.
3. **Transport Layer (Sprint 3)**: A network abstraction connecting backend state streams to the frontend.
4. **Frontend Stores**: Zustand stores (e.g., `useExecutionStore`) acting as deterministic sinks for the incoming event stream.

## Repository Structure

```text
.
├── backend/            # Python orchestration, agents, models, and transport logic
├── demo/               # Demo profiles and scenarios
├── docs/               # Architecture manifests and product specs
│   ├── architecture/
│   └── product/
├── frontend/           # Vite/React frontend acting as the IDE
├── .github/workflows/  # CI pipelines for frontend and backend
└── README.md
```

## Getting Started

### Backend Setup

1. Ensure Python 3.11+ is installed.
2. Navigate to the root directory.
3. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Setup

1. Ensure Node.js 20+ is installed.
2. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Run the Vite development server:
   ```bash
   npm run dev
   ```

## Development Workflow

Synapse enforces a strict "no fabricated state" rule. If the backend cannot emit a value, the frontend must not invent one. All state is strictly driven by the `EventBus` propagating canonical domain models. 

1. Write tests for backend logic before modifying the orchestrator.
2. Do not bypass the `EventBus` for cross-boundary communication.
3. Utilize `docs/architecture` for any significant architectural changes.

## Testing

**Backend:**
Run tests with `pytest`:
```bash
pytest backend/tests/
```

**Frontend:**
Validate types and build the client:
```bash
cd frontend
npm run build
```

## Roadmap

- **Sprint 3 (Upcoming)**: Transport networking (WebSockets/SSE) integrating the backend event stream with the frontend.
- **Future Sprints**: Advanced Execution Inspector, Timeline Replay, Consensus Visualization.

## Screenshots

*(Placeholder for future Mission Control UI screenshots)*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
