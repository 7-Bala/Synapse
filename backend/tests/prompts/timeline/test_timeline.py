import unittest

from schemas.agent import LiveSpecialistOutput
from services.structured_output import StructuredOutputValidator


class TestTimelinePrompt(unittest.TestCase):
    def validate_mock(self, mock_response: str) -> bool:
        parsed = StructuredOutputValidator.validate(mock_response, LiveSpecialistOutput)
        return parsed is not None and parsed.status.value in ["COMPLETE", "UNCERTAIN"]

    def test_perfectly_ordered(self):
        mock_response = """{
            "specialist": "TimelineAgent",
            "status": "COMPLETE",
            "finding": "HIGH - All evidence is perfectly chronologically aligned with clear causal links.",
            "reasoning": "Delta Nodes: [Event: Incident Start -> TS: 12:00 -> Source: Drone -> Conf: High]. Delta Edges: [Supports]. Graph Delta: Added new confirmed start time.",
            "confidence_reason": "official and verified timeline",
            "citations": ["evidence_1", "evidence_2"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_missing_timestamps(self):
        mock_response = """{
            "specialist": "TimelineAgent",
            "status": "UNCERTAIN",
            "finding": "LOW - Critical evidence lacks timestamps preventing ordering.",
            "reasoning": "Graph Delta: Unable to resolve missing timestamp.",
            "confidence_reason": "uncertain",
            "citations": [],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_contradictory_timestamps(self):
        mock_response = """{
            "specialist": "TimelineAgent",
            "status": "COMPLETE",
            "finding": "LOW - Sources provide conflicting timestamps for the same event.",
            "reasoning": "Delta Edges: [Contradicts]. Graph Delta: Source A claims 12:00, Source B claims 14:00.",
            "confidence_reason": "contradictory timestamps",
            "citations": ["evidence_3", "evidence_4"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_duplicate_reports(self):
        mock_response = """{
            "specialist": "TimelineAgent",
            "status": "COMPLETE",
            "finding": "MEDIUM - Duplicate reports mapping to the same temporal node.",
            "reasoning": "Delta Edges: [Duplicates]. Graph Delta: Merged duplicate events.",
            "confidence_reason": "partial duplicate resolution",
            "citations": ["evidence_5"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_impossible_ordering(self):
        mock_response = """{
            "specialist": "TimelineAgent",
            "status": "COMPLETE",
            "finding": "LOW - Effect precedes cause, violating causality.",
            "reasoning": "Graph Delta: Flagged temporal impossibility.",
            "confidence_reason": "conflict in causality",
            "citations": ["evidence_6"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))

    def test_incomplete_timelines(self):
        mock_response = """{
            "specialist": "TimelineAgent",
            "status": "UNCERTAIN",
            "finding": "LOW - Wide gaps in timeline prevent causal links.",
            "reasoning": "Graph Delta: Insufficiently constrained.",
            "confidence_reason": "uncertain gaps",
            "citations": ["evidence_7"],
            "latency_ms": 100,
            "tokens_in": 50,
            "tokens_out": 20,
            "prompt_version": "v1",
            "cache_hit": false
        }"""
        self.assertTrue(self.validate_mock(mock_response))


if __name__ == "__main__":
    unittest.main()
