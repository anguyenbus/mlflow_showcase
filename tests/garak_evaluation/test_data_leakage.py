"""Tests for data leakage evaluation runners."""

from garak_evaluation.shared.probe_manager import (
    get_available_probes,
    get_recommended_probes,
)
from garak_evaluation.shared.lifecycle_mapper import (
    get_category_lifecycle_mapping,
    get_owasp_category,
)


def test_data_leakage_probe_availability():
    """Test that data leakage probes are available."""
    probes = get_available_probes("data_leakage")
    assert len(probes) > 0
    assert "replay.Replay" in probes
    assert "hallucination.Hallucination" in probes
    assert "leakage.Leakage" in probes


def test_data_leakage_recommended_probes():
    """Test that recommended data leakage probes are correct."""
    recommended = get_recommended_probes("data_leakage", max_probes=3)
    assert len(recommended) <= 3
    assert "replay.Replay" in recommended


def test_data_leakage_owasp_mapping():
    """Test that data leakage maps to correct OWASP category."""
    owasp = get_owasp_category("data_leakage")
    assert owasp == "LLM06"

    mapping = get_category_lifecycle_mapping("data_leakage")
    assert mapping.owasp_category == "LLM06"


def test_data_leakage_lifecycle_phase():
    """Test that data leakage maps to correct lifecycle phase."""
    mapping = get_category_lifecycle_mapping("data_leakage")
    # Check that execution_analysis is in secondary phases
    assert any("execution" in phase or "analysis" in phase
               for phase in mapping.secondary_phases)
