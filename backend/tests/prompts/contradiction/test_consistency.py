import unittest

from schemas.agent import LiveSpecialistOutput
from services.structured_output import StructuredOutputValidator


class TestConsistencyPrompt(unittest.TestCase):
    def validate_mock(self, mock_response: str) -> bool:
        parsed = StructuredOutputValidator.validate(mock_response, LiveSpecialistOutput)
        return parsed is not None and parsed.status.value in ["COMPLETE", "UNCERTAIN"]

    def test_coherent_evidence_high_coherence(self):
        mock_response = """{
            "specialist": "ContradictionAgent",
            "status": "COMPLETE",
            "finding": "High evidence coherence across multiple clusters.",
            "reasoning": "Evidence Coherence Score: High.\\nAgreement Clusters: [Official, Visual] - Weight High - Agreement 0.9.\\nConflicting Clusters: None.\\nMissing Observations: None.\\nArbitration Readiness: Ready (Yes), Blocking Reason (None).",
            "confidence_reason": "official and verified coherence",
            "citations": ["ev_1", "ev_2"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_conflicting_evidence_low_coherence(self):
        mock_response = """{
            "specialist": "ContradictionAgent",
            "status": "COMPLETE",
            "finding": "Low evidence coherence due to direct conflict.",
            "reasoning": "Evidence Coherence Score: Low.\\nAgreement Clusters: None.\\nConflicting Clusters: [Official vs Social] - Weight High - Score 0.1.\\nMissing Observations: None.\\nArbitration Readiness: Ready (No), Blocking Reason (Direct Conflict), Next Best Evidence (Visual confirmation).",
            "confidence_reason": "contradictory evidence clusters",
            "citations": ["ev_3", "ev_4"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_missing_observations_arbitration_blocked(self):
        mock_response = """{
            "specialist": "ContradictionAgent",
            "status": "COMPLETE",
            "finding": "Critical expected observations are missing.",
            "reasoning": "Evidence Coherence Score: Medium.\\nAgreement Clusters: [Social].\\nConflicting Clusters: None.\\nMissing Observations: [Thermal Signature] - [Expected for explosions] - [Cannot confirm physical event without it].\\nArbitration Readiness: Ready (No), Blocking Reason (Missing vital telemetry), Next Best (Satellite thermal scan).",
            "confidence_reason": "uncertain missing evidence",
            "citations": ["ev_5"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_arbitration_ready(self):
        mock_response = """{
            "specialist": "ContradictionAgent",
            "status": "COMPLETE",
            "finding": "Sufficient coherence reached for arbitration.",
            "reasoning": "Evidence Coherence Score: High.\\nArbitration Readiness: Ready (Yes), Blocking Reason (None), Next Best Evidence (None), Estimated Gain (0.0).",
            "confidence_reason": "official complete evidence",
            "citations": ["ev_6", "ev_7"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))


if __name__ == "__main__":
    unittest.main()
