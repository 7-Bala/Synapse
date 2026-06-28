import unittest

from schemas.agent import LiveSpecialistOutput
from services.structured_output import StructuredOutputValidator


class TestSimulationPrompt(unittest.TestCase):
    def validate_mock(self, mock_response: str) -> bool:
        parsed = StructuredOutputValidator.validate(mock_response, LiveSpecialistOutput)
        return parsed is not None and parsed.status.value in ["COMPLETE", "UNCERTAIN"]

    def test_clear_best_action(self):
        mock_response = """{
            "specialist": "PredictionAgent",
            "status": "COMPLETE",
            "finding": "Holding operations is the safest action with highest confidence.",
            "reasoning": "Decision Matrix: Hold (Op: minimal, Fin: -$1M, Rep: none), Escalate, Reroute.\\nScenario Simulations: Best Case (Zero loss), Expected Case (Delay), Worst Case (Idle cost).\\nTime Horizons: Immediate (Pause), Medium-term (Resume).\\nRecommendation Confidence: Preferred (Hold) - Confidence 0.95 - Risk (Delay) - Benefit (Safety).",
            "confidence_reason": "clear and present danger verified",
            "citations": ["ev_1", "ev_2"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_ambiguous_actions(self):
        mock_response = """{
            "specialist": "PredictionAgent",
            "status": "UNCERTAIN",
            "finding": "Multiple actions have similar risk profiles, creating ambiguity.",
            "reasoning": "Decision Matrix: Hold vs Reroute have equal risk.\\nRecommendation Confidence: Preferred (None) - Confidence 0.4.",
            "confidence_reason": "ambiguous paths",
            "citations": ["ev_3"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_conflicting_actions(self):
        mock_response = """{
            "specialist": "PredictionAgent",
            "status": "COMPLETE",
            "finding": "Severe conflict between operational safety and financial impact.",
            "reasoning": "Decision Matrix: Pause (Safety high, Fin low) vs Continue (Safety low, Fin high).\\nRecommendation Confidence: Preferred (Pause) - Confidence 0.7 - Risk (Financial) - Benefit (Safety).",
            "confidence_reason": "conflicting action impacts",
            "citations": ["ev_4", "ev_5"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_high_uncertainty(self):
        mock_response = """{
            "specialist": "PredictionAgent",
            "status": "UNCERTAIN",
            "finding": "High uncertainty prevents reliable simulation of medium-term horizons.",
            "reasoning": "Scenario Simulations: Worst Case (Unbounded).\\nTime Horizons: Medium-term (Unknown).\\nRecommendation Confidence: Preferred (Escalate) - Confidence 0.2.",
            "confidence_reason": "high outcome volatility",
            "citations": ["ev_6"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_missing_evidence(self):
        mock_response = """{
            "specialist": "PredictionAgent",
            "status": "UNCERTAIN",
            "finding": "Missing telemetry prevents action recommendation.",
            "reasoning": "Decision Matrix: Insufficient data to evaluate Hold vs Continue.\\nRecommendation Confidence: Preferred (None) - Confidence 0.1.",
            "confidence_reason": "missing vital observations",
            "citations": ["ev_7"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))


if __name__ == "__main__":
    unittest.main()
