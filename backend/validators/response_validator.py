"""Response validation infrastructure."""

import json
from typing import Generic, Optional, Type, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class ValidationResult(Generic[T]):
    """Structured result wrapping validation success or specific failures."""

    def __init__(
        self,
        is_valid: bool,
        data: Optional[T] = None,
        error: Optional[str] = None,
    ):
        self.is_valid = is_valid
        self.data = data
        self.error = error


class ResponseValidator:
    """Validates raw model responses into structured Pydantic models."""

    def validate(
        self, response_text: Optional[str], schema: Type[T]
    ) -> ValidationResult[T]:
        """Validates strict JSON and converts it to a Pydantic model.

        Never throws exceptions upward; returns structured failures.

        Args:
            response_text: The raw JSON string from the model.
            schema: The Pydantic model class to validate against.

        Returns:
            ValidationResult: Contains either the parsed Pydantic model or an error.
        """
        if not response_text:
            return ValidationResult(
                is_valid=False, error="Received empty response text."
            )

        try:
            # Validate strict JSON
            parsed_json = json.loads(response_text)

            # Convert into Pydantic model
            data = schema.model_validate(parsed_json)
            return ValidationResult(is_valid=True, data=data)
        except json.JSONDecodeError as e:
            return ValidationResult(is_valid=False, error=f"Invalid JSON syntax: {e}")
        except ValidationError as e:
            return ValidationResult(
                is_valid=False, error=f"Schema validation failed: {e}"
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False, error=f"Unexpected validation error: {e}"
            )
