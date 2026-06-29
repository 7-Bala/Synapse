import os
import json
import asyncio
import sys

# Ensure backend is in path
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(base_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from generate_demo import main as generate_demo_main  # noqa: E402
from evaluation.golden_dataset import GoldenDataset  # noqa: E402
from evaluation.comparison_engine import (
    ExactComparator,
    NumericComparator,
    StructuralComparator,
    SemanticComparator,
)  # noqa: E402
from evaluation.evaluation_metrics import EvaluationMetrics  # noqa: E402


def get_artifact_path(directory: str, filename: str) -> str:
    """Returns the path to an artifact in the given directory."""
    path = os.path.join(directory, filename)
    return path if os.path.exists(path) else ""


async def run_evaluation():  # noqa: C901
    print("--- Starting Evaluation Runner ---")

    # 1. Run generation
    print("Generating scenario...")
    # generate_demo.main() writes to artifacts/ and metrics/
    await generate_demo_main()

    # 2. Locate generated artifacts
    artifacts_dir = os.path.join(base_dir, "artifacts", "current")
    metrics_dir = os.path.join(base_dir, "artifacts", "current")

    events_path = get_artifact_path(artifacts_dir, "events.json")
    manifest_path = get_artifact_path(artifacts_dir, "manifest.json")
    prompt_bundle_path = get_artifact_path(artifacts_dir, "prompt_bundle.json")
    metrics_path = get_artifact_path(metrics_dir, "metrics.json")

    if not all([events_path, manifest_path, prompt_bundle_path, metrics_path]):
        print("ERROR: Could not find all generated artifacts.")
        sys.exit(1)

    with open(events_path, "r", encoding="utf-8") as f:
        actual_events = json.load(f)
    with open(manifest_path, "r", encoding="utf-8") as f:
        actual_manifest = json.load(f)
    with open(prompt_bundle_path, "r", encoding="utf-8") as f:
        actual_prompt_bundle = json.load(f)
    with open(metrics_path, "r", encoding="utf-8") as f:
        json.load(f)

    # Find decision and trace from events
    actual_decision = {}
    for event in actual_events:
        if (
            event.get("event_type") == "specialist_finished"
            and event.get("specialist_name") == "ConsensusAgent"
        ):
            actual_decision = event.get("output", {})
            event.get("output", {}).get("decision_trace", {})

    golden_dir = os.path.join(backend_dir, "golden", "supply_chain")
    if not os.path.exists(golden_dir) or not os.listdir(golden_dir):
        print("Golden Dataset Status: NOT INITIALIZED")
        print("Run `python evaluation/update_golden.py --approve` to initialize.")
        return

    golden = GoldenDataset(golden_dir)
    metrics = EvaluationMetrics(os.path.join(backend_dir, "evaluation_output"))

    print("Comparing artifacts against golden dataset...")

    # --- Compare Decision (Exact + Structural) ---
    if golden.expected_decision:
        res = ExactComparator.compare(
            golden.expected_decision.get("decision"),
            actual_decision.get("decision"),
            "decision.decision",
        )
        if not res.passed:
            metrics.record_failure("decision", res.message)

        res = ExactComparator.compare(
            golden.expected_decision.get("status"),
            actual_decision.get("status"),
            "decision.status",
        )
        if not res.passed:
            metrics.record_failure("decision", res.message)

        # Confidence (Numeric)
        expected_conf = golden.expected_decision.get("confidence", 0.0)
        actual_conf = actual_decision.get("confidence", 0.0)
        res = NumericComparator.compare(
            expected_conf, actual_conf, tolerance=0.02, field_path="decision.confidence"
        )
        if not res.passed:
            metrics.record_failure("confidence", res.message)

        # Findings / Reasoning (Structural & Semantic Stub)
        expected_findings = golden.expected_decision.get("findings", [])
        actual_findings = actual_decision.get("findings", [])
        res = StructuralComparator.compare(
            expected_findings, actual_findings, "decision.findings"
        )
        if not res.passed:
            metrics.record_failure("decision", res.message)

        expected_reasoning = golden.expected_decision.get("rationale", "")
        actual_reasoning = actual_decision.get("rationale", "")
        res_sem = SemanticComparator.compare(
            expected_reasoning, actual_reasoning, "decision.rationale"
        )
        if res_sem.warning:
            metrics.record_warning("decision", res_sem.message)

    # --- Compare Manifest (Exact) ---
    if golden.expected_manifest:
        # Schema
        res = ExactComparator.compare(
            golden.expected_manifest.get("configuration", {}).get("schema_version"),
            actual_manifest.get("configuration", {}).get("schema_version"),
            "manifest.schema_version",
        )
        if not res.passed:
            metrics.record_failure("architecture", res.message)

        # Replay Hash (if configured as exact)
        # Note: timestamps and replay ID might change if we don't fix time, so we compare intermediate hashes
        expected_events_hash = golden.expected_manifest.get("artifact_hashes", {}).get(
            "events_json"
        )
        actual_events_hash = actual_manifest.get("artifact_hashes", {}).get(
            "events_json"
        )
        res = ExactComparator.compare(
            expected_events_hash, actual_events_hash, "manifest.events_hash"
        )
        if not res.passed:
            metrics.record_failure("hash", res.message)

    # --- Compare Prompts (Exact) ---
    if golden.expected_prompt_bundle:
        # Check versions
        res = StructuralComparator.compare(
            golden.expected_prompt_bundle, actual_prompt_bundle, "prompt_bundle"
        )
        if not res.passed:
            metrics.record_failure("prompt", res.message)

    # --- Compare Metrics (Numeric) ---
    if golden.expected_metrics:
        # Latency check (e.g., 5% tolerance on average latency)
        pass  # We can implement specific checks if latency is recorded

    metrics_file = metrics.export()
    from evaluation.report_generator import ReportGenerator

    rg = ReportGenerator(backend_dir)
    md_file = rg.generate_markdown(metrics_file)
    print(f"Evaluation complete. JSON at {metrics_file}, MD at {md_file}")

    if metrics.metrics["overall_status"] == "FAIL":
        print("EVALUATION FAILED")
        for f in metrics.metrics["failures"]:
            print(f" - {f['message']}")
        sys.exit(1)
    else:
        print("EVALUATION PASSED")
        for w in metrics.metrics["warnings"]:
            print(f" - WARNING: {w['message']}")


if __name__ == "__main__":
    asyncio.run(run_evaluation())
