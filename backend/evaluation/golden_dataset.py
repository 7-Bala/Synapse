import json
import os
from typing import Any, Dict


class GoldenDataset:
    def __init__(self, golden_dir: str):
        self.golden_dir = golden_dir
        self.expected_events: Dict[str, Any] = {}
        self.expected_decision: Dict[str, Any] = {}
        self.expected_trace: Dict[str, Any] = {}
        self.expected_metrics: Dict[str, Any] = {}
        self.expected_manifest: Dict[str, Any] = {}
        self.expected_prompt_bundle: Dict[str, Any] = {}
        self._load()

    def _load(self):
        self.expected_events = self._load_file("expected_events.json")
        self.expected_decision = self._load_file("expected_decision.json")
        self.expected_trace = self._load_file("expected_trace.json")
        self.expected_metrics = self._load_file("expected_metrics.json")
        self.expected_manifest = self._load_file("expected_manifest.json")
        self.expected_prompt_bundle = self._load_file("expected_prompt_bundle.json")

    def _load_file(self, filename: str) -> Dict[str, Any]:
        file_path = os.path.join(self.golden_dir, filename)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
