"""Tests for result analysis utilities."""

from garak_evaluation.shared.result_parser import (
    GarakEvaluationSummary,
    GarakResultParser,
    ProbeResult,
)
from garak_evaluation.shared.analysis import (
    calculate_aggregated_metrics,
    classify_vulnerability_severity,
)
import tempfile
import json


def test_jsonl_parsing():
    """Test that JSONL results can be parsed."""
    # Create a temporary JSONL file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        # Write sample JSONL entries
        f.write('{"probe": "test.Probe", "detector": "keyword", "total": 10, "passed": 8, "failed": 2}\n')
        f.write('{"probe": "test.Probe2", "detector": "classifier", "total": 10, "passed": 6, "failed": 4}\n')
        temp_path = f.name

    try:
        parser = GarakResultParser(temp_path)
        summary = parser.get_summary()

        assert summary.total_probes == 2
        assert summary.total_tests == 20
        assert summary.overall_pass_rate == 0.7
    finally:
        import os
        os.unlink(temp_path)


def test_metric_aggregation():
    """Test that metrics are aggregated correctly."""
    probe_results = [
        ProbeResult(
            probe_name="probe1",
            detector_type="keyword",
            pass_rate=0.8,
            fail_rate=0.2,
            total_tests=10,
            passed_tests=8,
            failed_tests=2,
            detector_score=0.8,
        ),
        ProbeResult(
            probe_name="probe2",
            detector_type="classifier",
            pass_rate=0.6,
            fail_rate=0.4,
            total_tests=10,
            passed_tests=6,
            failed_tests=4,
            detector_score=0.6,
        ),
    ]

    metrics = calculate_aggregated_metrics(probe_results)

    assert metrics["total_probes"] == 2
    assert metrics["total_tests"] == 20
    assert metrics["overall_pass_rate"] == 0.7
    assert metrics["overall_fail_rate"] == 0.3


def test_severity_classification():
    """Test that vulnerability severity is classified correctly."""
    assert classify_vulnerability_severity(0.6) == "HIGH"
    assert classify_vulnerability_severity(0.4) == "MEDIUM"
    assert classify_vulnerability_severity(0.2) == "LOW"
    assert classify_vulnerability_severity(0.05) == "MINIMAL"


def test_detector_score_analysis():
    """Test that detector scores are analyzed correctly."""
    probe_results = [
        ProbeResult(
            probe_name="probe1",
            detector_type="keyword",
            pass_rate=0.8,
            fail_rate=0.2,
            total_tests=10,
            passed_tests=8,
            failed_tests=2,
            detector_score=0.85,
        ),
    ]

    metrics = calculate_aggregated_metrics(probe_results)

    assert "avg_detector_score" in metrics
    assert metrics["avg_detector_score"] == 0.85
