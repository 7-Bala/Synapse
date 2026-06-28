"""Prompt builder infrastructure for the Synapse backend."""

import os
from typing import Any, Dict, List


class PromptBuilder:
    """Builds provider-ready messages from markdown templates."""

    def __init__(self, templates_dir: str):
        """Initializes the PromptBuilder.

        Args:
            templates_dir: The base directory where markdown templates are stored.
        """
        self.templates_dir = templates_dir

    def build_messages(
        self, template_filename: str, variables: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Loads a template, injects variables, and returns standard messages.

        Args:
            template_filename: The name of the template file to load.
            variables: Variables to inject into the template via format().

        Returns:
            List[Dict[str, str]]: A list of message dictionaries (e.g., role/content).
        """
        template_path = os.path.join(self.templates_dir, template_filename)
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Inject runtime variables
        try:
            formatted_content = content.format(**variables)
        except KeyError as e:
            # If variables are missing, we could fail safely, but formatting expects them.
            raise ValueError(f"Missing expected prompt variable: {e}")

        # Return a provider-ready message format (assuming system prompt for simplicity)
        return [{"role": "system", "content": formatted_content}]
