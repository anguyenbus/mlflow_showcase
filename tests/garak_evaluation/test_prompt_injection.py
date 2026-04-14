"""Tests for prompt injection evaluation runners."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def test_prompt_injection_config_parsing():
    """Test that prompt injection YAML config can be parsed."""
    from garak_evaluation.shared.probe_manager import generate_yaml_config

    # Create a temporary config
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        config = generate_yaml_config(
            probe_names=["encoding.B64NestedInjection"],
            model_name="glm-5-flash",
            output_path=f.name,
        )

    # Verify config structure
    assert "generators" in config
    assert "probes" in config
    assert "encoding.B64NestedInjection" in config["probes"]
    assert config["generators"][0]["name"] == "glm-5-flash"


def test_prompt_injection_probe_selection():
    """Test that prompt injection probes can be selected."""
    from garak_evaluation.shared.probe_manager import (
        get_available_probes,
        get_recommended_probes,
    )

    probes = get_available_probes("prompt_injection")
    assert len(probes) > 0
    assert "encoding.B64NestedInjection" in probes

    recommended = get_recommended_probes("prompt_injection", max_probes=3)
    assert len(recommended) <= 3


def test_prompt_injection_lifecycle_mapping():
    """Test that prompt injection maps to correct lifecycle phase."""
    from garak_evaluation.shared.lifecycle_mapper import (
        get_category_lifecycle_mapping,
        get_owasp_category,
    )

    mapping = get_category_lifecycle_mapping("prompt_injection")
    assert mapping.owasp_category == "LLM01"
    assert "attack" in mapping.primary_phase

    owasp = get_owasp_category("prompt_injection")
    assert owasp == "LLM01"


def test_prompt_injection_result_parsing():
    """Test that prompt injection results can be parsed."""
    from garak_evaluation.shared.result_parser import (
        GarakEvaluationSummary,
        ProbeResult,
    )

    # Create mock probe results
    results = [
        ProbeResult(
            probe_name="encoding.B64NestedInjection",
            detector_type="keyword",
            pass_rate=0.8,
            fail_rate=0.2,
            total_tests=10,
            passed_tests=8,
            failed_tests=2,
            detector_score=0.8,
        ),
        ProbeResult(
            probe_name="web_injection.DirectIndirectInjection",
            detector_type="keyword",
            pass_rate=0.6,
            fail_rate=0.4,
            total_tests=10,
            passed_tests=6,
            failed_tests=4,
            detector_score=0.6,
        ),
    ]

    # Create summary
    summary = GarakEvaluationSummary(
        total_probes=2,
        total_tests=20,
        overall_pass_rate=0.7,
        overall_fail_rate=0.3,
        probe_results=results,
        vulnerable_probes=["web_injection.DirectIndirectInjection"],
    )

    # Verify summary
    assert summary.total_probes == 2
    assert summary.overall_pass_rate == 0.7
    assert len(summary.vulnerable_probes) == 1
