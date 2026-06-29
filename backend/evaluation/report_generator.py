import json
import os

class ReportGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def generate_markdown(self, metrics_file: str, filename: str = "evaluation_summary.md") -> str:
        if not os.path.exists(metrics_file):
            return ""
            
        with open(metrics_file, "r", encoding="utf-8") as f:
            metrics = json.load(f)
            
        lines = []
        lines.append("# Evaluation Summary")
        lines.append("")
        
        status = metrics.get("overall_status", "UNKNOWN")
        lines.append(f"**Overall Score:** {metrics.get('pass_rate', 0.0) * 100}%")
        lines.append(f"**Status:** {status}")
        lines.append("")
        
        if metrics.get("failures"):
            lines.append("## Failures")
            for fail in metrics["failures"]:
                lines.append(f"- **{fail['category']}**: {fail['message']}")
            lines.append("")
            
        if metrics.get("warnings"):
            lines.append("## Warnings")
            for warn in metrics["warnings"]:
                lines.append(f"- **{warn['category']}**: {warn['message']}")
            lines.append("")
            
        lines.append("## Regressions")
        lines.append(f"- Decision Regressions: {metrics.get('decision_regressions', 0)}")
        lines.append(f"- Confidence Regressions: {metrics.get('confidence_regressions', 0)}")
        lines.append(f"- Replay Regressions: {metrics.get('replay_regressions', 0)}")
        lines.append(f"- Architecture Regressions: {metrics.get('architecture_regressions', 0)}")
        lines.append(f"- Prompt Regressions: {metrics.get('prompt_regressions', 0)}")
        lines.append(f"- Performance Regressions: {metrics.get('performance_regressions', 0)}")
        lines.append(f"- Hash Regressions: {metrics.get('hash_regressions', 0)}")
        lines.append("")
        
        lines.append("## Recommendations")
        if status == "FAIL":
            lines.append("Review the exact and numeric failures above. A production AI system should not fail because wording changed; it fails because behavior changed.")
        else:
            lines.append("All tests passed. System is stable.")
            
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
            
        return file_path
