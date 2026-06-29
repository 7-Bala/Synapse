#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

run_gate() {
  local label="$1"
  shift
  echo
  echo "==> ${label}"
  "$@"
}

run_gate "ruff" ruff check .
run_gate "black" black --check .
run_gate "mypy" mypy --explicit-package-bases .
run_gate "pytest" pytest
run_gate "smoke test" python3 backend/smoke_test.py
run_gate "generate demo" python3 backend/generate_demo.py
run_gate "replay validator" python3 backend/validators/replay_validator.py
run_gate "architecture validator" python3 backend/validators/architecture_validator.py

echo
echo "==> operational validator"
set +e
python3 backend/validators/operational_validator.py
operational_exit=$?
set -e
if [[ "$operational_exit" -gt 1 ]]; then
  echo "Operational validator failed with exit code ${operational_exit}."
  exit "$operational_exit"
fi

run_gate "evaluation runner" python3 backend/evaluation/evaluation_runner.py
run_gate "benchmark runner" python3 backend/evaluation/benchmark_runner.py

echo
echo "==> refresh operational validator summary"
set +e
python3 backend/validators/operational_validator.py --summary >/tmp/synapse_operational_summary.txt 2>&1
final_operational_exit=$?
set -e
if [[ "$final_operational_exit" -gt 1 ]]; then
  cat /tmp/synapse_operational_summary.txt
  exit "$final_operational_exit"
fi

python3 - <<'PY'
import json
from pathlib import Path

report_path = Path("artifacts/current/operational_report.json")
benchmark_path = Path("benchmark_report.json")
report = json.loads(report_path.read_text(encoding="utf-8"))
benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))

print()
print("Release Summary")
print(f"Implementation: {report['implementation_status']}")
print(f"Environment: {report['environment_status']}")
print(f"Deployment Decision: {report['deployment_decision']}")
print(f"Operational Score: {report['operational_score']}")
print(
    "Benchmark: "
    f"avg_latency={benchmark['average_latency']:.3f}s "
    f"failure_rate={benchmark['failure_rate']:.1%} "
    f"determinism={benchmark['determinism_rate']:.2f}"
)

env_warnings = report.get("environment_warnings", [])
if env_warnings:
    print("Environmental warnings:")
    for warning in env_warnings:
        print(f"- {warning}")
else:
    print("Environmental warnings: none")

impl_warnings = report.get("implementation_warnings", [])
if impl_warnings:
    print("Implementation warnings:")
    for warning in impl_warnings:
        print(f"- {warning}")
else:
    print("Implementation warnings: none")
PY
