"""Utility to load versioned prompts."""

from pathlib import Path


class PromptLoader:
    """Loads versioned markdown prompts from disk."""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)

    def load(self, specialist: str, version: str) -> str:
        """Loads a prompt like 'source_v1.md'.

        Args:
            specialist: Name of the specialist (e.g. 'source', 'vision').
            version: Version string (e.g. 'v1').
        """
        filename = f"{specialist.lower()}_{version}.md"
        filepath = self.base_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Prompt {filename} not found at {self.base_dir}")

        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
