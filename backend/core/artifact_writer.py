"""Transactional Artifact Writer for robust artifact generation."""

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any


class TransactionalArtifactWriter:
    """Manages atomic generation, staging, and promotion of replay artifacts."""

    def __init__(self, artifacts_dir: str):
        self.artifacts_dir = Path(artifacts_dir)
        self.current_dir = self.artifacts_dir / "current"
        self.archive_dir = self.artifacts_dir / "archive"
        self.staging_dir = self.artifacts_dir / ".staging"

        # Ensure directories exist
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.current_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        self._ensure_clean_staging()

    def _ensure_clean_staging(self) -> None:
        """Removes the staging directory if it exists and creates a fresh one."""
        if self.staging_dir.exists():
            shutil.rmtree(self.staging_dir)
        self.staging_dir.mkdir(parents=True, exist_ok=True)

    def write_json(self, filename: str, content: Any) -> str:
        """Writes JSON content to the staging directory and returns its SHA-256 hash."""
        filepath = self.staging_dir / filename

        # Format as string if it isn't already
        if isinstance(content, (dict, list)):
            content_str = json.dumps(content, indent=2)
        else:
            content_str = str(content)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content_str)

        return hashlib.sha256(content_str.encode("utf-8")).hexdigest()

    def write_text(self, filename: str, content_str: str) -> str:
        """Writes string content to the staging directory and returns its SHA-256 hash."""
        filepath = self.staging_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content_str)

        return hashlib.sha256(content_str.encode("utf-8")).hexdigest()

    def _archive_current(self) -> None:
        """Moves the current directory contents to an archive folder."""
        if not any(self.current_dir.iterdir()):
            return

        # Find the next replay number
        archive_num = 1
        while (self.archive_dir / f"replay_{archive_num:03d}").exists():
            archive_num += 1

        archive_target = self.archive_dir / f"replay_{archive_num:03d}"

        # Move current to archive
        shutil.move(str(self.current_dir), str(archive_target))
        # Recreate empty current directory
        self.current_dir.mkdir(parents=True, exist_ok=True)

    def commit(self) -> None:
        """Validates staging and atomically promotes it to current."""
        # Validate that all required files exist
        required_files = [
            "events.json",
            "manifest.json",
            "metrics.json",
            "prompt_bundle.json",
            "replay_certificate.json"
        ]

        for file in required_files:
            if not (self.staging_dir / file).exists():
                self.rollback()
                raise FileNotFoundError(f"Validation failed: missing required artifact {file}")

        # Archive the existing current artifacts
        self._archive_current()

        # Atomically rename staging to current
        if self.current_dir.exists():
            os.rmdir(self.current_dir)

        os.rename(self.staging_dir, self.current_dir)

    def rollback(self) -> None:
        """Discards the staging directory."""
        if self.staging_dir.exists():
            shutil.rmtree(self.staging_dir)
