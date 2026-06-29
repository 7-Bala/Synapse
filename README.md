# Synapse v2.0

Synapse is a deterministic enterprise AI decision platform with replay generation, provenance validation, evaluation tooling, and operational readiness reporting.

## Overview

The backend is organized around a frozen specialist pipeline:
- specialists generate structured outputs
- orchestrator manages tick execution
- consensus produces the final decision
- replay artifacts capture deterministic execution
- validators verify provenance, architecture, and operational readiness

Architecture and contract constraints are documented in [docs/ARCHITECTURE_FROZEN.md](docs/ARCHITECTURE_FROZEN.md).

## Installation

1. Create a Python environment.
2. Install dependencies from `requirements.txt`.
3. Optional: configure `.env` for live provider access.

## Offline Mode

Offline mode is the default release-validation mode.

- No API key required
- No network dependency
- Deterministic provider responses behind the provider layer
- Compatible with replay, evaluation, and benchmark validation

## Live Mode

Live provider execution is opt-in.

Enable one of:
- `SYNAPSE_ENABLE_LIVE_PROVIDER=true`
- `enable_live_provider=true` in environment-backed settings

If live mode is enabled, `CEREBRAS_API_KEY` must be available.

## Common Commands

### Run validations

```bash
ruff check .
black --check .
mypy --explicit-package-bases .
pytest
```

### Generate a deterministic replay

```bash
python3 backend/generate_demo.py
```

### Run evaluation

```bash
python3 backend/evaluation/evaluation_runner.py
```

### Run benchmarks

```bash
python3 backend/evaluation/benchmark_runner.py
```

### Run the operational validator

```bash
python3 backend/validators/operational_validator.py
```

### Run the full release gate

```bash
./scripts/release_validation.sh
```

## Release Validation

The release script runs:
- linting
- formatting checks
- type checking
- test suite
- smoke validation
- demo generation
- replay validation
- architecture validation
- operational validation
- evaluation
- benchmarking

It stops on mandatory failures and prints a concise release summary at completion.

## Documentation

- [docs/ARCHITECTURE_FROZEN.md](docs/ARCHITECTURE_FROZEN.md)
- [docs/RELEASE_v2.0.md](docs/RELEASE_v2.0.md)
- [CHANGELOG.md](CHANGELOG.md)
