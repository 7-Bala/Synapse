import unittest
from schemas.agent import LiveSpecialistOutput
from services.structured_output import StructuredOutputValidator


class TestVisionPrompt(unittest.TestCase):
    def validate_mock(self, mock_response: str) -> bool:
        parsed = StructuredOutputValidator.validate(mock_response, LiveSpecialistOutput)
        return parsed is not None and parsed.status.value in ["COMPLETE", "UNCERTAIN"]

    def test_clear_image(self):
        mock_response = """{
            "specialist": "VisionAgent",
            "status": "COMPLETE",
            "finding": "Vessel observed at port.",
            "reasoning": "Markdown structured ledger... Entities: [Vessel -> Location -> Port -> High]",
            "confidence_reason": "official and verified clarity",
            "citations": ["evidence_1"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_ambiguous_image(self):
        mock_response = """{
            "specialist": "VisionAgent",
            "status": "UNCERTAIN",
            "finding": "Indistinguishable physical shapes.",
            "reasoning": "Uncertainty: Low resolution imagery prevents identification.",
            "confidence_reason": "uncertain",
            "citations": ["evidence_2"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_contradictory_image(self):
        mock_response = """{
            "specialist": "VisionAgent",
            "status": "COMPLETE",
            "finding": "CCTV contradicts drone imagery.",
            "reasoning": "Contradicts: Drone claims fire, CCTV shows normal operations.",
            "confidence_reason": "direct physical contradiction",
            "citations": ["evidence_3", "evidence_4"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_missing_image(self):
        mock_response = """{
            "specialist": "VisionAgent",
            "status": "UNCERTAIN",
            "finding": "No visual evidence provided.",
            "reasoning": "Uncertainty: Missing image data.",
            "confidence_reason": "uncertain",
            "citations": [],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))


if __name__ == "__main__":
    unittest.main()
