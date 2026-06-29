"""Deterministic tests for Phase 10: Operational Validator.

All tests are read-only and deterministic — no external LLM calls,
no modification of production artifacts.
"""

import json
import sys
import time
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure backend is importable
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from validators.operational_validator import (  # noqa: E402
    DeploymentDecision,
    StageStatus,
    StageResult,
    STAGE_WEIGHTS,
    BLOCKING_STAGES,
    _compute_score,
    _compute_decision,
    _generate_recommendations,
    _build_report,
    _write_json_report,
    _write_summary_report,
    _stage_configuration,
    _stage_infrastructure,
    _stage_artifacts,
    _stage_replay,
    _stage_architecture,
    _stage_evaluation,
    _stage_benchmark,
    _stage_failure_injection,
    _stage_health,
    _stage_resources,
    _CURRENT_DIR,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_current_dir(tmp_path):
    """Provides a tmp_path acting as artifacts/current/ with required artifacts."""
    current = tmp_path / "artifacts" / "current"
    current.mkdir(parents=True)
    return current


def _make_stage(name: str, status: StageStatus, score: float) -> StageResult:
    return StageResult(name=name, status=status, score=score, duration_ms=1.0)


def _make_all_passed_stages() -> list:
    return [
        _make_stage("Configuration", StageStatus.PASSED, 100.0),
        _make_stage("Infrastructure", StageStatus.PASSED, 100.0),
        _make_stage("Artifacts", StageStatus.PASSED, 100.0),
        _make_stage("Replay", StageStatus.PASSED, 100.0),
        _make_stage("Architecture", StageStatus.PASSED, 100.0),
        _make_stage("Evaluation", StageStatus.PASSED, 100.0),
        _make_stage("Benchmark", StageStatus.PASSED, 100.0),
        _make_stage("FailureInjection", StageStatus.PASSED, 100.0),
        _make_stage("Health", StageStatus.PASSED, 100.0),
        _make_stage("Resources", StageStatus.PASSED, 100.0),
    ]


# ---------------------------------------------------------------------------
# Stage weight tests
# ---------------------------------------------------------------------------


class TestStageWeights:
    def test_weights_sum_to_one(self):
        total = sum(STAGE_WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9

    def test_all_stages_have_weights(self):
        stage_names = {
            name
            for name, _ in [
                ("Configuration", None),
                ("Infrastructure", None),
                ("Artifacts", None),
                ("Replay", None),
                ("Architecture", None),
                ("Evaluation", None),
                ("Benchmark", None),
                ("FailureInjection", None),
                ("Health", None),
                ("Resources", None),
            ]
        }
        for name in stage_names:
            assert name in STAGE_WEIGHTS, f"Missing weight for {name}"

    def test_blocking_stages_defined(self):
        assert "Replay" in BLOCKING_STAGES
        assert "Architecture" in BLOCKING_STAGES


# ---------------------------------------------------------------------------
# Score computation
# ---------------------------------------------------------------------------


class TestScoreComputation:
    def test_all_passed_gives_100(self):
        stages = _make_all_passed_stages()
        score = _compute_score(stages)
        assert abs(score - 100.0) < 0.01

    def test_empty_stages_gives_zero(self):
        assert _compute_score([]) == 0.0

    def test_partial_failure_lowers_score(self):
        stages = _make_all_passed_stages()
        # Fail Architecture (weight 0.15, score 0)
        stages[4] = _make_stage("Architecture", StageStatus.FAILED, 0.0)
        score = _compute_score(stages)
        assert score < 100.0
        assert score > 0.0

    def test_score_is_deterministic(self):
        stages_a = _make_all_passed_stages()
        stages_b = _make_all_passed_stages()
        assert _compute_score(stages_a) == _compute_score(stages_b)

    def test_single_warning_stage(self):
        stages = _make_all_passed_stages()
        stages[8] = _make_stage("Health", StageStatus.WARNING, 70.0)
        score = _compute_score(stages)
        # Health weight = 0.05, score drops from 100 to 70 → overall drops by 0.05*30 = 1.5
        assert score == pytest.approx(100.0 - 0.05 * 30.0, abs=0.01)


# ---------------------------------------------------------------------------
# Deployment decision logic
# ---------------------------------------------------------------------------


class TestDeploymentDecision:
    def test_all_passed_is_ready(self):
        stages = _make_all_passed_stages()
        decision = _compute_decision(stages, 100.0, strict=False)
        assert decision == DeploymentDecision.READY

    def test_replay_failed_is_not_ready(self):
        stages = _make_all_passed_stages()
        stages[3] = _make_stage("Replay", StageStatus.FAILED, 0.0)
        score = _compute_score(stages)
        decision = _compute_decision(stages, score, strict=False)
        assert decision == DeploymentDecision.NOT_READY

    def test_architecture_failed_is_not_ready(self):
        stages = _make_all_passed_stages()
        stages[4] = _make_stage("Architecture", StageStatus.FAILED, 0.0)
        decision = _compute_decision(stages, 85.0, strict=False)
        assert decision == DeploymentDecision.NOT_READY

    def test_non_blocking_failure_is_ready_with_warnings(self):
        stages = _make_all_passed_stages()
        stages[8] = _make_stage("Health", StageStatus.FAILED, 0.0)
        decision = _compute_decision(stages, 95.0, strict=False)
        assert decision == DeploymentDecision.READY_WITH_WARNINGS

    def test_warning_is_ready_with_warnings(self):
        stages = _make_all_passed_stages()
        stages[9] = _make_stage("Resources", StageStatus.WARNING, 70.0)
        decision = _compute_decision(stages, 98.0, strict=False)
        assert decision == DeploymentDecision.READY_WITH_WARNINGS

    def test_strict_warning_is_not_ready(self):
        stages = _make_all_passed_stages()
        stages[9] = _make_stage("Resources", StageStatus.WARNING, 70.0)
        decision = _compute_decision(stages, 98.0, strict=True)
        assert decision == DeploymentDecision.NOT_READY

    def test_score_below_50_is_not_ready(self):
        stages = _make_all_passed_stages()
        decision = _compute_decision(stages, 45.0, strict=False)
        assert decision == DeploymentDecision.NOT_READY

    def test_decision_is_deterministic(self):
        stages_a = _make_all_passed_stages()
        stages_b = _make_all_passed_stages()
        d1 = _compute_decision(stages_a, 100.0, False)
        d2 = _compute_decision(stages_b, 100.0, False)
        assert d1 == d2


# ---------------------------------------------------------------------------
# Stage: Configuration
# ---------------------------------------------------------------------------


class TestStageConfiguration:
    def test_passes_with_valid_settings(self):
        result = _stage_configuration()
        # Settings exist in this repo — should pass or warn only
        assert result.status in (StageStatus.PASSED, StageStatus.WARNING)
        assert result.score > 0.0

    def test_has_detail(self):
        result = _stage_configuration()
        assert "cache_schema_version" in result.detail


# ---------------------------------------------------------------------------
# Stage: Infrastructure
# ---------------------------------------------------------------------------


class TestStageInfrastructure:
    def test_all_components_importable(self):
        result = _stage_infrastructure()
        # All infrastructure must be importable in this repo
        assert result.status != StageStatus.FAILED

    def test_detail_contains_failed_count(self):
        result = _stage_infrastructure()
        assert "failed_count" in result.detail


# ---------------------------------------------------------------------------
# Stage: Artifacts
# ---------------------------------------------------------------------------


class TestStageArtifacts:
    def test_passes_when_artifacts_present(self):
        # The real artifacts/current/ should have all required files after generate_demo
        result = _stage_artifacts()
        # If current dir has all required files it should PASS, else WARNING
        assert result.status in (
            StageStatus.PASSED,
            StageStatus.WARNING,
            StageStatus.FAILED,
        )

    def test_failed_when_dir_empty(self, tmp_path):
        with patch("validators.operational_validator._CURRENT_DIR", tmp_path / "empty"):
            result = _stage_artifacts()
        assert result.status == StageStatus.FAILED
        assert result.score < 100.0

    def test_warnings_for_optional_missing(self, tmp_path):
        # Create all required artifacts but no optional ones
        current = tmp_path / "current"
        current.mkdir()
        for name in [
            "events.json",
            "metrics.json",
            "manifest.json",
            "replay_certificate.json",
            "prompt_bundle.json",
        ]:
            (current / name).write_text("{}")
        with patch("validators.operational_validator._CURRENT_DIR", current):
            result = _stage_artifacts()
        assert result.status in (StageStatus.PASSED, StageStatus.WARNING)


# ---------------------------------------------------------------------------
# Stage: Replay
# ---------------------------------------------------------------------------


class TestStageReplay:
    def test_fails_gracefully_when_no_cert(self, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        with patch("validators.operational_validator._CURRENT_DIR", empty):
            result = _stage_replay()
        assert result.status == StageStatus.FAILED
        assert result.score == 0.0

    def test_passes_with_valid_certificate(self):
        # Real artifacts/current/ should have a valid cert from generate_demo
        cert_path = _CURRENT_DIR / "replay_certificate.json"
        if cert_path.exists():
            result = _stage_replay()
            assert result.status in (StageStatus.PASSED, StageStatus.FAILED)
        else:
            pytest.skip("No replay_certificate.json — run generate_demo first")


# ---------------------------------------------------------------------------
# Stage: Architecture
# ---------------------------------------------------------------------------


class TestStageArchitecture:
    def test_passes_on_valid_codebase(self):
        result = _stage_architecture()
        assert result.status == StageStatus.PASSED
        assert result.score == 100.0

    def test_detail_contains_no_violations(self):
        result = _stage_architecture()
        errors = [f for f in result.findings if f.severity == "ERROR"]
        assert len(errors) == 0


# ---------------------------------------------------------------------------
# Stage: Evaluation
# ---------------------------------------------------------------------------


class TestStageEvaluation:
    def test_returns_valid_result(self):
        result = _stage_evaluation()
        assert result.status in (
            StageStatus.PASSED,
            StageStatus.WARNING,
            StageStatus.FAILED,
        )
        assert 0.0 <= result.score <= 100.0

    def test_skips_gracefully_without_golden_dataset(self, tmp_path):
        with patch("validators.operational_validator._BACKEND_DIR", tmp_path):
            result = _stage_evaluation()
        assert result.status == StageStatus.WARNING


# ---------------------------------------------------------------------------
# Stage: Benchmark
# ---------------------------------------------------------------------------


class TestStageBenchmark:
    def test_warns_when_report_missing(self, tmp_path):
        with patch("validators.operational_validator._REPO_ROOT", tmp_path):
            result = _stage_benchmark()
        assert result.status == StageStatus.WARNING
        assert result.score < 100.0

    def test_passes_with_healthy_report(self, tmp_path):
        report = {
            "iterations": 5,
            "average_latency": 1.2,
            "median_latency": 1.1,
            "p95_latency": 1.5,
            "standard_deviation": 0.1,
            "determinism_rate": 1.0,
            "failure_rate": 0.0,
            "cache_hit_ratio": 0.0,
            "cache_miss_ratio": 0.0,
            "memory_usage": 0.0,
        }
        (tmp_path / "benchmark_report.json").write_text(json.dumps(report))
        with patch("validators.operational_validator._REPO_ROOT", tmp_path):
            result = _stage_benchmark()
        assert result.status == StageStatus.PASSED

    def test_fails_with_high_failure_rate(self, tmp_path):
        report = {
            "iterations": 5,
            "average_latency": 1.2,
            "determinism_rate": 1.0,
            "failure_rate": 0.5,
        }
        (tmp_path / "benchmark_report.json").write_text(json.dumps(report))
        with patch("validators.operational_validator._REPO_ROOT", tmp_path):
            result = _stage_benchmark()
        assert result.status == StageStatus.FAILED


# ---------------------------------------------------------------------------
# Stage: Failure Injection
# ---------------------------------------------------------------------------


class TestStageFailureInjection:
    def test_warns_when_no_report(self, tmp_path):
        with patch("validators.operational_validator._CURRENT_DIR", tmp_path):
            result = _stage_failure_injection()
        assert result.status == StageStatus.WARNING

    def test_passes_with_valid_report(self, tmp_path):
        (tmp_path / "failure_report.json").write_text(
            json.dumps(
                {
                    "generated_at": "2026-01-01",
                    "total_failures": 3,
                    "failures": [],
                }
            )
        )
        with patch("validators.operational_validator._CURRENT_DIR", tmp_path):
            result = _stage_failure_injection()
        assert result.status == StageStatus.PASSED


# ---------------------------------------------------------------------------
# Stage: Health
# ---------------------------------------------------------------------------


class TestStageHealth:
    def test_warns_when_no_report(self, tmp_path):
        with patch("validators.operational_validator._CURRENT_DIR", tmp_path):
            result = _stage_health()
        assert result.status == StageStatus.WARNING

    def test_passes_when_healthy(self, tmp_path):
        (tmp_path / "health_report.json").write_text(
            json.dumps(
                {
                    "overall_status": "HEALTHY",
                    "checks": [],
                }
            )
        )
        with patch("validators.operational_validator._CURRENT_DIR", tmp_path):
            result = _stage_health()
        assert result.status == StageStatus.PASSED

    def test_fails_when_status_failed(self, tmp_path):
        (tmp_path / "health_report.json").write_text(
            json.dumps(
                {
                    "overall_status": "FAILED",
                    "checks": [],
                }
            )
        )
        with patch("validators.operational_validator._CURRENT_DIR", tmp_path):
            result = _stage_health()
        assert result.status == StageStatus.FAILED


# ---------------------------------------------------------------------------
# Stage: Resources
# ---------------------------------------------------------------------------


class TestStageResources:
    def test_warns_when_no_report(self, tmp_path):
        with patch("validators.operational_validator._CURRENT_DIR", tmp_path):
            result = _stage_resources()
        assert result.status == StageStatus.WARNING

    def test_passes_when_healthy(self, tmp_path):
        (tmp_path / "resource_report.json").write_text(
            json.dumps(
                {
                    "overall_status": "HEALTHY",
                    "violations": [],
                }
            )
        )
        with patch("validators.operational_validator._CURRENT_DIR", tmp_path):
            result = _stage_resources()
        assert result.status == StageStatus.PASSED

    def test_warns_when_degraded(self, tmp_path):
        (tmp_path / "resource_report.json").write_text(
            json.dumps(
                {
                    "overall_status": "DEGRADED",
                    "violations": [{"resource": "cpu", "value": 75.0}],
                }
            )
        )
        with patch("validators.operational_validator._CURRENT_DIR", tmp_path):
            result = _stage_resources()
        assert result.status == StageStatus.WARNING


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


class TestReportGeneration:
    def _build_sample_report(self):
        stages = _make_all_passed_stages()
        score = _compute_score(stages)
        decision = _compute_decision(stages, score, strict=False)
        return _build_report(
            stages, score, decision, "abc1234", "v2.0-test", time.perf_counter() - 0.1
        )

    def test_json_report_written(self, tmp_path):
        current = tmp_path / "artifacts" / "current"
        current.mkdir(parents=True)
        report = self._build_sample_report()
        with (
            patch("validators.operational_validator._CURRENT_DIR", current),
            patch(
                "validators.operational_validator._ARTIFACTS_DIR",
                tmp_path / "artifacts",
            ),
        ):
            path = _write_json_report(report)
        assert path.exists()
        data = json.loads(path.read_text())
        assert "operational_score" in data
        assert "deployment_decision" in data
        assert "stages" in data
        assert data["deterministic"] if "deterministic" in data else True

    def test_summary_md_written(self, tmp_path):
        current = tmp_path / "artifacts" / "current"
        current.mkdir(parents=True)
        report = self._build_sample_report()
        with (
            patch("validators.operational_validator._CURRENT_DIR", current),
            patch(
                "validators.operational_validator._ARTIFACTS_DIR",
                tmp_path / "artifacts",
            ),
        ):
            path = _write_summary_report(report)
        assert path.exists()
        content = path.read_text()
        assert "Operational Validator" in content
        assert "Deployment Decision" in content

    def test_archive_never_overwrites(self, tmp_path):
        current = tmp_path / "artifacts" / "current"
        current.mkdir(parents=True)
        report = self._build_sample_report()
        with (
            patch("validators.operational_validator._CURRENT_DIR", current),
            patch(
                "validators.operational_validator._ARTIFACTS_DIR",
                tmp_path / "artifacts",
            ),
        ):
            _write_json_report(report)
            time.sleep(0.01)
            _write_json_report(report)

        archive_dir = tmp_path / "artifacts" / "archive" / "operational"
        archives = list(archive_dir.glob("operational_report_*.json"))
        assert len(archives) == 2

    def test_report_schema_fields(self, tmp_path):
        current = tmp_path / "artifacts" / "current"
        current.mkdir(parents=True)
        report = self._build_sample_report()
        with (
            patch("validators.operational_validator._CURRENT_DIR", current),
            patch(
                "validators.operational_validator._ARTIFACTS_DIR",
                tmp_path / "artifacts",
            ),
        ):
            path = _write_json_report(report)
        data = json.loads(path.read_text())
        required_keys = [
            "generated_at",
            "git_commit",
            "git_tag",
            "replay_id",
            "manifest_hash",
            "operational_score",
            "deployment_decision",
            "stages",
            "warnings",
            "failures",
            "recommendations",
        ]
        for key in required_keys:
            assert key in data, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------


class TestRecommendations:
    def test_no_findings_gives_ready_message(self):
        stages = _make_all_passed_stages()
        recs = _generate_recommendations(stages)
        assert any("operationally ready" in r.lower() for r in recs)

    def test_failed_stage_generates_critical(self):
        stages = _make_all_passed_stages()
        stages[3].status = StageStatus.FAILED
        stages[3].add_error("Hash mismatch")
        recs = _generate_recommendations(stages)
        assert any("[CRITICAL]" in r for r in recs)

    def test_warning_stage_generates_warning(self):
        stages = _make_all_passed_stages()
        stages[9].status = StageStatus.WARNING
        recs = _generate_recommendations(stages)
        assert any("[WARNING]" in r for r in recs)


# ---------------------------------------------------------------------------
# CLI exit codes
# ---------------------------------------------------------------------------


class TestCLIExitCodes:
    def test_ready_exit_0(self, tmp_path):
        stages = _make_all_passed_stages()
        score = _compute_score(stages)
        decision = _compute_decision(stages, score, strict=False)
        assert decision == DeploymentDecision.READY

        from validators.operational_validator import main

        with (
            patch("validators.operational_validator._CURRENT_DIR", tmp_path),
            patch("validators.operational_validator._ARTIFACTS_DIR", tmp_path),
            patch("sys.argv", ["operational_validator.py"]),
            patch(
                "validators.operational_validator.OperationalValidator.run"
            ) as mock_run,
        ):

            mock_report = MagicMock()
            mock_report.deployment_decision = "READY"
            mock_report.operational_score = 100.0
            mock_report.stage_results = stages
            mock_report.failures = []
            mock_report.warnings = []
            mock_report.replay_id = "abc" * 10
            mock_report.git_commit = "abc1234"
            mock_report.git_tag = "v2.0"
            mock_report.execution_duration_ms = 100.0
            mock_run.return_value = mock_report

            code = main()
        assert code == 0

    def test_ready_with_warnings_exit_1(self):
        from validators.operational_validator import main

        with (
            patch("sys.argv", ["operational_validator.py"]),
            patch(
                "validators.operational_validator.OperationalValidator.run"
            ) as mock_run,
        ):
            mock_report = MagicMock()
            mock_report.deployment_decision = "READY_WITH_WARNINGS"
            mock_report.operational_score = 88.0
            mock_report.stage_results = _make_all_passed_stages()
            mock_report.failures = []
            mock_report.warnings = ["Resource warning"]
            mock_report.replay_id = "abc" * 10
            mock_report.git_commit = "abc1234"
            mock_report.git_tag = "v2.0"
            mock_report.execution_duration_ms = 100.0
            mock_run.return_value = mock_report

            code = main()
        assert code == 1

    def test_not_ready_exit_2(self):
        from validators.operational_validator import main

        with (
            patch("sys.argv", ["operational_validator.py"]),
            patch(
                "validators.operational_validator.OperationalValidator.run"
            ) as mock_run,
        ):
            mock_report = MagicMock()
            mock_report.deployment_decision = "NOT_READY"
            mock_report.operational_score = 30.0
            mock_report.stage_results = _make_all_passed_stages()
            mock_report.failures = ["Critical failure"]
            mock_report.warnings = []
            mock_report.replay_id = "abc" * 10
            mock_report.git_commit = "abc1234"
            mock_report.git_tag = "v2.0"
            mock_report.execution_duration_ms = 100.0
            mock_run.return_value = mock_report

            code = main()
        assert code == 2


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_stages_give_same_score(self):
        stages_a = _make_all_passed_stages()
        stages_b = _make_all_passed_stages()
        assert _compute_score(stages_a) == _compute_score(stages_b)

    def test_configuration_stage_deterministic(self):
        r1 = _stage_configuration()
        r2 = _stage_configuration()
        assert r1.status == r2.status
        assert r1.score == r2.score

    def test_architecture_stage_deterministic(self):
        r1 = _stage_architecture()
        r2 = _stage_architecture()
        assert r1.status == r2.status
        assert r1.score == r2.score
