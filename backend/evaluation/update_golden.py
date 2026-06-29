import os
import sys
import shutil
import argparse

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def find_latest_artifact(directory: str, prefix: str, suffix: str = ".json") -> str:
    if not os.path.exists(directory):
        return ""
    files = [f for f in os.listdir(directory) if f.startswith(prefix) and f.endswith(suffix)]
    if not files:
        return ""
    files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
    return os.path.join(directory, files[0])

def main():
    parser = argparse.ArgumentParser(description="Update Golden Dataset")
    parser.add_argument("--approve", action="store_true", help="Approve replacement of the baseline.")
    args = parser.parse_args()

    backend_dir = os.path.join(base_dir, "backend")
    golden_dir = os.path.join(backend_dir, "golden", "supply_chain")
    artifacts_dir = os.path.join(base_dir, "artifacts")
    metrics_dir = os.path.join(base_dir, "metrics")

    events_path = find_latest_artifact(artifacts_dir, "events_supply_chain_")
    manifest_path = find_latest_artifact(artifacts_dir, "manifest_")
    prompt_bundle_path = find_latest_artifact(artifacts_dir, "prompt_bundle_")
    metrics_path = find_latest_artifact(metrics_dir, "metrics_report_")

    if not all([events_path, manifest_path, prompt_bundle_path, metrics_path]):
        print("ERROR: Could not find all generated artifacts to seed golden dataset.")
        sys.exit(1)

    if not args.approve:
        print("Golden Dataset Update Preview:")
        print(f" - Events: {os.path.basename(events_path)} -> expected_events.json")
        print(f" - Manifest: {os.path.basename(manifest_path)} -> expected_manifest.json")
        print(f" - Prompt Bundle: {os.path.basename(prompt_bundle_path)} -> expected_prompt_bundle.json")
        print(f" - Metrics: {os.path.basename(metrics_path)} -> expected_metrics.json")
        print("\nTo update, run with --approve")
        sys.exit(0)

    os.makedirs(golden_dir, exist_ok=True)

    shutil.copy2(events_path, os.path.join(golden_dir, "expected_events.json"))
    shutil.copy2(manifest_path, os.path.join(golden_dir, "expected_manifest.json"))
    shutil.copy2(prompt_bundle_path, os.path.join(golden_dir, "expected_prompt_bundle.json"))
    shutil.copy2(metrics_path, os.path.join(golden_dir, "expected_metrics.json"))

    # Extract decision and trace from events
    import json
    with open(events_path, "r", encoding="utf-8") as f:
        events = json.load(f)
        for event in events:
            if event.get("event_type") == "specialist_finished" and event.get("specialist_name") == "ConsensusAgent":
                decision_output = event.get("output", {})
                with open(os.path.join(golden_dir, "expected_decision.json"), "w", encoding="utf-8") as out:
                    json.dump(decision_output, out, indent=2)

                decision_trace = decision_output.get("decision_trace", {})
                with open(os.path.join(golden_dir, "expected_trace.json"), "w", encoding="utf-8") as out:
                    json.dump(decision_trace, out, indent=2)

    print("SUCCESS: Golden dataset updated.")

    with open(os.path.join(backend_dir, "golden_update_report.md"), "w") as f:
        f.write("# Golden Dataset Update Report\n")
        f.write("Baseline updated successfully via --approve.\n")

if __name__ == "__main__":
    main()
