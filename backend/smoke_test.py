"""Smoke test script for Synapse AI infrastructure."""

import os
from unittest.mock import MagicMock

from pydantic import BaseModel, Field

from prompts.base import PromptBuilder
from services.cerebras import CerebrasService
from validators.response_validator import ResponseValidator


class MockAgentOutput(BaseModel):
    """A dummy schema for smoke testing."""

    status: str = Field(..., description="The status of the test")
    confidence: float = Field(..., description="Confidence score")


def run_smoke_test() -> None:
    """Runs the smoke test pipeline."""
    # 1. Setup mock template
    prompts_dir = os.path.join(os.path.dirname(__file__), "prompts", "system")
    os.makedirs(prompts_dir, exist_ok=True)
    template_path = os.path.join(prompts_dir, "smoke.md")
    with open(template_path, "w", encoding="utf-8") as f:
        f.write("You are a helpful assistant. The topic is {topic}.")

    # 2. Prompt Builder
    builder = PromptBuilder(templates_dir=prompts_dir)
    messages = builder.build_messages("smoke.md", variables={"topic": "testing"})
    print("--- Built Messages ---")
    print(messages)

    # 3. Cerebras Service (mocked for testing without API key)
    service = CerebrasService()

    # Mock the API response to avoid actual network calls during smoke test
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = (
        '{"status": "success", "confidence": 0.99}'
    )

    service._client.chat.completions.create = MagicMock(return_value=mock_response)  # type: ignore[method-assign]

    print("\n--- Calling Cerebras (Mocked) ---")
    raw_response = service.generate_structured_response(
        messages=messages, response_format={"type": "json_object"}
    )
    print(f"Raw Response: {raw_response}")

    # 4. Validate Response
    validator = ResponseValidator()
    print("\n--- Validating Response ---")
    result = validator.validate(raw_response, MockAgentOutput)

    if result.is_valid and result.data:
        print("\nValidated JSON (Pydantic Model):")
        print(result.data.model_dump_json(indent=2))
        print("\nSmoke Test PASSED!")
    else:
        print(f"\nSmoke Test FAILED: {result.error}")
        exit(1)


if __name__ == "__main__":
    run_smoke_test()
