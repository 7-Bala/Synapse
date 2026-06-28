"""Utility to validate structured output."""

import json
from typing import Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class StructuredOutputValidator:
    """Validates raw LLM JSON output against a Pydantic schema."""

    @staticmethod
    def validate(raw_json: Optional[str], schema: Type[T]) -> Optional[T]:
        """Validates the raw json against the schema.

        Returns the parsed model, or None if validation fails.
        """
        if not raw_json:
            return None

        try:
            # Sometime LLMs wrap json in markdown code blocks
            clean_json = raw_json.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]

            parsed = json.loads(clean_json.strip())
            return schema(**parsed)
        except (json.JSONDecodeError, ValidationError) as e:
            # We never crash generation. We just return None, which translates to UNCERTAIN.
            print(f"Validation error: {e}")
            return None
