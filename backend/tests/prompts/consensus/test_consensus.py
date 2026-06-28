import unittest

from schemas.agent import LiveSpecialistOutput
from services.structured_output import StructuredOutputValidator


class TestConsensusPrompt(unittest.TestCase):
    def validate_mock(self, mock_response: str) -> bool:
        parsed = StructuredOutputValidator.validate(mock_response, LiveSpecialistOutput)
        return parsed is not None and parsed.status.value in ["COMPLETE", "UNCERTAIN"]

    def test_unanimous_agreement(self):
        mock_response = """{
            "specialist": "ConsensusAgent",
            "status": "COMPLETE",
            "finding": "All specialists unanimously support publishing the alert.",
            "reasoning": "Machine Output: {'decision': 'Publish', 'confidence': 1.0, 'human_review_required': false, 'dominant_factor': 'Simulation recommendation', 'blocking_reason': 'None'}.\\nHuman Explanation: Strongest support from Visual and Source confirmation. Alternatives rejected due to high certainty.\\nDecision Trace: Evidence -> Visual (Confirmed) -> Consistency (High) -> Simulation (Publish) -> Weighting (1.0) -> Publish.",
            "confidence_reason": "deterministic weighting flawless",
            "citations": ["ev_1"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_conflicting_specialists(self):
        mock_response = """{
            "specialist": "ConsensusAgent",
            "status": "COMPLETE",
            "finding": "Conflicting evidence led to Hold decision.",
            "reasoning": "Machine Output: {'decision': 'Hold', 'confidence': 0.6, 'human_review_required': true, 'dominant_factor': 'Missing/Uncertain evidence', 'blocking_reason': 'Too many uncertain specialists'}.\\nHuman Explanation: Human review required because Visual conflicts with Source. Recommend fetching thermal telemetry.\\nDecision Trace: Evidence -> Conflict -> Weighting (0.6) -> Hold.",
            "confidence_reason": "conflicting weights triggered review",
            "citations": ["ev_2"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_low_confidence(self):
        mock_response = """{
            "specialist": "ConsensusAgent",
            "status": "UNCERTAIN",
            "finding": "Weighting indicates low confidence, deferring to human.",
            "reasoning": "Machine Output: {'decision': 'Hold', 'confidence': 0.2, 'human_review_required': true, 'dominant_factor': 'Missing/Uncertain evidence', 'blocking_reason': 'Too many uncertain specialists'}.\\nHuman Explanation: Severe lack of telemetry across all sensors. Recommend fetching direct field report.\\nDecision Trace: Uncertainty -> Weighting (0.2) -> Hold.",
            "confidence_reason": "majority uncertain",
            "citations": ["ev_3"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))


if __name__ == "__main__":
    unittest.main()
