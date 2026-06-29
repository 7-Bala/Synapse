"""Utility to load versioned prompts."""

import hashlib
from pathlib import Path
from typing import Dict, Any


class PromptLoader:
    """Loads versioned markdown prompts from disk and maintains provenance metadata."""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self._prompts: Dict[str, str] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._load_all_prompts()

    def _load_all_prompts(self) -> None:
        """Loads all prompts into memory and computes metadata."""
        if not self.base_dir.exists():
            return

        for filepath in self.base_dir.glob("*.md"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            filename = filepath.name
            sha256_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            char_count = len(content)
            # Simple whitespace estimation
            estimated_tokens = len(content.split())

            # Extract version from filename (e.g. source_v1.md -> v1)
            # Default to v1 if no version suffix
            version = "v1"
            name_parts = filepath.stem.split("_")
            if len(name_parts) > 1 and name_parts[-1].startswith("v"):
                version = name_parts[-1]

            self._prompts[filename] = content
            self._metadata[filename] = {
                "filename": filename,
                "version": version,
                "sha256": sha256_hash,
                "characters": char_count,
                "estimated_tokens": estimated_tokens,
            }

    def load(self, specialist: str, version: str) -> str:
        """Loads a prompt like 'source_v1.md'.

        Args:
            specialist: Name of the specialist (e.g. 'source', 'vision').
            version: Version string (e.g. 'v1').
        """
        filename = f"{specialist.lower()}_{version}.md"

        if filename not in self._prompts:
            raise FileNotFoundError(
                f"Prompt {filename} not found in preloaded cache at {self.base_dir}"
            )

        return self._prompts[filename]

    def get_all_metadata(self) -> list[Dict[str, Any]]:
        """Returns metadata for all loaded prompts."""
        return list(self._metadata.values())
