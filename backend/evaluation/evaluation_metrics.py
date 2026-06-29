import json
import os
from typing import Dict, Any

class EvaluationMetrics:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.metrics: Dict[str, Any] = {
            "overall_status": "PASS",
            "pass_rate": 1.0,
            "decision_regressions": 0,
            "confidence_regressions": 0,
            "replay_regressions": 0,
            "architecture_regressions": 0,
            "prompt_regressions": 0,
            "performance_regressions": 0,
            "hash_regressions": 0,
            "failures": [],
            "warnings": []
        }

    def record_failure(self, category: str, message: str) -> None:
        self.metrics["overall_status"] = "FAIL"
        if f"{category}_regressions" in self.metrics:
            self.metrics[f"{category}_regressions"] += 1
        self.metrics["failures"].append({"category": category, "message": message})

    def record_warning(self, category: str, message: str) -> None:
        self.metrics["warnings"].append({"category": category, "message": message})

    def export(self, filename: str = "evaluation_report.json") -> str:
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

        file_path = os.path.join(self.output_dir, filename)

        # Calculate pass rate based on failures
        if self.metrics["failures"]:
            self.metrics["pass_rate"] = 0.0

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.metrics, f, indent=2)

        return file_path
