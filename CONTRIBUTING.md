# Contributing to Synapse

Thank you for your interest in contributing to Synapse! We welcome all contributions, from bug reports to feature implementation.

## Development Workflow

1. **Clone the repository** and install dependencies for both the backend and frontend.
2. **Backend**: Python 3.11+. Install requirements via `pip install -r requirements.txt`.
3. **Frontend**: Node 20+. Install dependencies via `npm install` inside the `frontend` directory.
4. **Create a branch**: Make your changes in a new branch.
5. **Run tests**: Ensure `pytest backend/tests/` passes.
6. **Submit a Pull Request**: Provide a clear description of the problem and your solution.

## Architecture Guidelines

- Do not bypass the `EventBus` or `Orchestrator` lifecycle for state updates.
- Synapse is an AI operating system. The frontend must act as a transparent window into backend execution states. Never fabricate UI data.
- Ensure all architecture modifications are documented in `docs/architecture/`.

## Code Style

- Format backend Python code with `ruff`.
- Format frontend TypeScript code using `eslint` and `prettier`.
