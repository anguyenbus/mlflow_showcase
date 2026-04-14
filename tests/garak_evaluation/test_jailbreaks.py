"""Tests for jailbreaks evaluation runners."""

from garak_evaluation.shared.probe_manager import (
    get_available_probes,
    get_recommended_probes,
    validate_probe_name,
)
from garak_evaluation.shared.lifecycle_mapper import (
    get_category_lifecycle_mapping,
    get_owasp_category,
)


def test_jailbreaks_probe_availability():
    """Test that jailbreaks probes are available."""
    probes = get_available_probes("jailbreaks")
    assert len(probes) > 0
    assert "dan.DAN" in probes
    assert "grandma.Grandma" in probes
    assert "goodside.Goodside" in probes


def test_jailbreaks_recommended_probes():
    """Test that recommended jailbreaks probes are correct."""
    recommended = get_recommended_probes("jailbreaks", max_probes=3)
    assert len(recommended) <= 3
    assert "dan.DAN" in recommended


def test_jailbreaks_owasp_mapping():
    """Test that jailbreaks map to correct OWASP category."""
    owasp = get_owasp_category("jailbreaks")
    assert owasp == "LLM01"

    mapping = get_category_lifecycle_mapping("jailbreaks")
    assert mapping.owasp_category == "LLM01"


def test_jailbreaks_probe_validation():
    """Test that jailbreaks probe names are valid."""
    assert validate_probe_name("dan.DAN") is True
    assert validate_probe_name("grandma.Grandma") is True
    assert validate_probe_name("goodside.Goodside") is True
    assert validate_probe_name("invalid.Probe") is False
