"""Tests for malicious content evaluation runners."""

from garak_evaluation.shared.probe_manager import (
    get_available_probes,
    get_recommended_probes,
)
from garak_evaluation.shared.lifecycle_mapper import (
    get_category_lifecycle_mapping,
    get_owasp_category,
)


def test_malicious_content_probe_availability():
    """Test that malicious content probes are available."""
    probes = get_available_probes("malicious_content")
    assert len(probes) > 0
    assert "malwaregen.MalwareGen" in probes
    assert "harmful.HarmfulContent" in probes


def test_malicious_content_recommended_probes():
    """Test that recommended malicious content probes are correct."""
    recommended = get_recommended_probes("malicious_content", max_probes=3)
    assert len(recommended) <= 3
    assert "malwaregen.MalwareGen" in recommended


def test_malicious_content_owasp_mapping():
    """Test that malicious content maps to correct OWASP category."""
    owasp = get_owasp_category("malicious_content")
    assert owasp == "LLM03"

    mapping = get_category_lifecycle_mapping("malicious_content")
    assert mapping.owasp_category == "LLM03"


def test_malicious_content_safety_guidance():
    """Test that safety guidance is documented."""
    from garak_evaluation.shared.lifecycle_mapper import get_remediation_guidance

    guidance = get_remediation_guidance("malicious_content", "HIGH")
    assert "immediate" in guidance
    assert len(guidance) > 0
