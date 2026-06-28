import unittest
from services.structured_output import StructuredOutputValidator
from schemas.agent import LiveSpecialistOutput


class TestSourcePrompt(unittest.TestCase):
    def test_source_prompt_schema(self):
        # A mock response from LLM
        mock_response = """{
            "specialist": "SourceAgent",
            "status": "COMPLETE",
            "finding": "Source is highly reliable based on cross-verification.",
            "reasoning": "Markdown structured ledger... supporting evidence: port logs...",
            "confidence_reason": "official and verified",
            "citations": ["evidence_1", "evidence_2"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""

        parsed = StructuredOutputValidator.validate(mock_response, LiveSpecialistOutput)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.status.value, "COMPLETE")
        self.assertTrue(len(parsed.citations) > 0)
        self.assertEqual(parsed.prompt_version, "v1")

    def test_source_prompt_missing_fields(self):
        # Missing required finding
        mock_response = """{
            "specialist": "SourceAgent",
            "status": "COMPLETE",
            "reasoning": "Markdown structured ledger...",
            "confidence_reason": "official and verified",
            "citations": ["evidence_1"]
        }"""
        parsed = StructuredOutputValidator.validate(mock_response, LiveSpecialistOutput)
        self.assertIsNone(parsed)


if __name__ == "__main__":
    unittest.main()
