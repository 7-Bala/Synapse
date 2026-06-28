"""Utility to validate a generated demo replay artifact."""

import json
import os
import sys


def validate_replay(events_path: str) -> bool:
    """Validates the structure and ordering of a replay file."""
    if not os.path.exists(events_path):
        print(f"Error: {events_path} not found.")
        return False

    with open(events_path, "r", encoding="utf-8") as f:
        try:
            events = json.load(f)
        except json.JSONDecodeError:
            print("Error: Invalid JSON.")
            return False

    if not isinstance(events, list):
        print("Error: Replay must be a list of events.")
        return False

    if len(events) == 0:
        print("Warning: Replay is empty.")
        return True

    # Validate ordering by timestamp_ms
    last_ts = -1
    for idx, ev in enumerate(events):
        if "timestamp_ms" not in ev:
            print(f"Error: Event {idx} missing timestamp_ms")
            return False
        if "event_type" not in ev:
            print(f"Error: Event {idx} missing event_type")
            return False
        if "evidence_cycle" not in ev:
            print(f"Error: Event {idx} missing evidence_cycle")
            return False

        ts = ev["timestamp_ms"]
        if ts < last_ts:
            print(
                f"Error: Event {idx} is out of chronological order (ts {ts} < last {last_ts})"
            )
            return False
        last_ts = ts

    print("Replay validation passed successfully.")
    return True


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    frontend_events = os.path.join(base_dir, "frontend", "public", "events.json")
    if not validate_replay(frontend_events):
        sys.exit(1)
    sys.exit(0)
