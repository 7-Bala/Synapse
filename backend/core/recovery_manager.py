"""Recovery Manager for validating and recovering artifacts."""

import json
import shutil
from pathlib import Path
from typing import Optional

from validators.replay_validator import ReplayValidator


class RecoveryManager:
    """Detects, validates, quarantines, and recovers replay artifacts."""

    def __init__(self, artifacts_dir: str):
        self.artifacts_dir = Path(artifacts_dir)
        self.current_dir = self.artifacts_dir / "current"
        self.archive_dir = self.artifacts_dir / "archive"
        self.staging_dir = self.artifacts_dir / ".staging"
        self.quarantine_dir = self.artifacts_dir / "quarantine"

        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        # Metrics dir for the validator (though artifacts now hold metrics too)
        self.metrics_dir = self.current_dir

        self.validator = ReplayValidator(str(self.artifacts_dir), str(self.metrics_dir))

    def _generate_report(
        self, status: str, details: str, recovered_from: Optional[str] = None
    ) -> None:
        """Publishes an operational report of the recovery action."""
        report = {
            "status": status,
            "details": details,
            "recovered_from": recovered_from,
        }
        report_path = self.artifacts_dir / "recovery_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    def _quarantine(self, source_dir: Path, reason: str) -> None:
        """Moves corrupted or incomplete artifacts to quarantine."""
        if not source_dir.exists() or not any(source_dir.iterdir()):
            return

        quarantine_num = 1
        while (self.quarantine_dir / f"quarantined_{quarantine_num:03d}").exists():
            quarantine_num += 1

        target = self.quarantine_dir / f"quarantined_{quarantine_num:03d}"
        shutil.move(str(source_dir), str(target))

        # Write reason
        with open(target / "quarantine_reason.txt", "w", encoding="utf-8") as f:
            f.write(reason)

    def _recover_from_archive(self) -> bool:
        """Attempts to restore the latest valid replay from archive."""
        if not self.archive_dir.exists():
            return False

        replays = sorted(
            [
                d
                for d in self.archive_dir.iterdir()
                if d.is_dir() and d.name.startswith("replay_")
            ],
            reverse=True,
        )
        for replay in replays:
            if self.validator.validate_certificate(str(replay)):
                # Found a valid replay, restore it
                if self.current_dir.exists():
                    shutil.rmtree(self.current_dir)
                shutil.copytree(str(replay), str(self.current_dir))
                return True

        return False

    def recover(self) -> bool:
        """
        Observes filesystem state, cleans up incomplete generations,
        and validates/recovers current state.
        Returns True if the system is in a healthy state (or successfully recovered).
        """
        # 1. Cleanup staging
        if self.staging_dir.exists():
            if any(self.staging_dir.iterdir()):
                self._quarantine(
                    self.staging_dir, "Incomplete generation (left in staging)"
                )
            if self.staging_dir.exists():
                shutil.rmtree(self.staging_dir)

        # 2. Check current directory
        if not self.current_dir.exists() or not any(self.current_dir.iterdir()):
            recovered = self._recover_from_archive()
            if recovered:
                self._generate_report(
                    "RECOVERED",
                    "Current dir was empty, recovered from archive.",
                    "archive",
                )
                return True
            else:
                self._generate_report(
                    "FAILED", "Current dir empty and no valid archives found."
                )
                return False

        # 3. Validate current artifacts
        if self.validator.validate_certificate(str(self.current_dir)):
            self._generate_report("HEALTHY", "Current artifacts are valid.", "current")
            return True
        else:
            # Current is corrupted
            self._quarantine(self.current_dir, "Current artifacts failed validation.")
            self.current_dir.mkdir(parents=True, exist_ok=True)

            recovered = self._recover_from_archive()
            if recovered:
                self._generate_report(
                    "RECOVERED",
                    "Current artifacts corrupted, recovered from archive.",
                    "archive",
                )
                return True
            else:
                self._generate_report(
                    "FAILED", "Current artifacts corrupted and no valid archives found."
                )
                return False
