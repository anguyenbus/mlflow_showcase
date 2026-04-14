"""
CPH Sec AI Red Team Lifecycle mapping utilities.

This module provides mappings between Garak probes, OWASP LLM Top 10
categories, and the CPH Sec AI Red Team Lifecycle phases.
"""

from dataclasses import dataclass
from typing import Any, Final

from beartype import beartype
from rich.table import Table

# NOTE: Import console output utilities
from garak_evaluation.shared.console_output import console, print_section_header

# CPH Sec AI Red Team Lifecycle phases
LIFECYCLE_PHASES: Final[dict[str, dict[str, Any]]] = {
    "planning_reconnaissance": {
        "name": "Planning and Reconnaissance",
        "description": "Identify targets, gather intelligence, define scope",
        "activities": [
            "Identify LLM applications to test",
            "Map model capabilities and interfaces",
            "Review documentation and API specs",
            "Define testing boundaries and rules of engagement",
        ],
    },
    "threat_modeling": {
        "name": "Threat Modeling and Prioritization",
        "description": "Categorize threats, prioritize attack vectors",
        "activities": [
            "Map to OWASP LLM Top 10",
            "Identify high-risk probe categories",
            "Prioritize testing based on impact",
            "Document threat assumptions",
        ],
    },
    "attack_identification": {
        "name": "Attack Vector Identification",
        "description": "Select probes, configure test scenarios",
        "activities": [
            "Select appropriate Garak probes",
            "Configure test parameters",
            "Prepare test data and payloads",
            "Set up monitoring and logging",
        ],
    },
    "execution_analysis": {
        "name": "Execution and Analysis",
        "description": "Run evaluations, analyze results",
        "activities": [
            "Execute Garak probes",
            "Monitor evaluation progress",
            "Parse and analyze results",
            "Identify successful attacks",
        ],
    },
    "reporting_remediation": {
        "name": "Reporting and Remediation",
        "description": "Document findings, recommend fixes",
        "activities": [
            "Generate vulnerability reports",
            "Classify severity levels",
            "Provide remediation guidance",
            "Track remediation progress",
        ],
    },
}

# Mapping of probe categories to lifecycle phases
CATEGORY_TO_LIFECYCLE: Final[dict[str, dict[str, str]]] = {
    "prompt_injection": {
        "primary_phase": "attack_identification",
        "secondary_phases": ["execution_analysis", "reporting_remediation"],
        "owasp": "LLM01",
    },
    "jailbreaks": {
        "primary_phase": "attack_identification",
        "secondary_phases": ["execution_analysis", "reporting_remediation"],
        "owasp": "LLM01",
    },
    "data_leakage": {
        "primary_phase": "attack_identification",
        "secondary_phases": ["execution_analysis", "reporting_remediation"],
        "owasp": "LLM06",
    },
    "malicious_content": {
        "primary_phase": "attack_identification",
        "secondary_phases": ["execution_analysis", "reporting_remediation"],
        "owasp": "LLM03",
    },
}


@beartype
@dataclass(frozen=True, slots=True)
class LifecycleMapping:
    """
    Mapping of a probe category to lifecycle phases.

    Attributes:
        category: Probe category name.
        primary_phase: Primary lifecycle phase.
        secondary_phases: List of secondary phases.
        owasp_category: OWASP LLM Top 10 category.

    """

    category: str
    primary_phase: str
    secondary_phases: list[str]
    owasp_category: str


@beartype
def get_lifecycle_phase(phase_id: str) -> dict[str, Any]:
    """
    Get information about a lifecycle phase.

    Args:
        phase_id: Phase identifier (e.g., "planning_reconnaissance").

    Returns:
        Dictionary with phase information.

    Raises:
        ValueError: If phase_id is not recognized.

    Example:
        >>> phase = get_lifecycle_phase("planning_reconnaissance")
        >>> phase["name"]
        'Planning and Reconnaissance'

    """
    if phase_id not in LIFECYCLE_PHASES:
        available = ", ".join(LIFECYCLE_PHASES.keys())
        raise ValueError(
            f"Unknown phase: {phase_id}. Available: {available}"
        )

    return LIFECYCLE_PHASES[phase_id].copy()


@beartype
def get_category_lifecycle_mapping(category: str) -> LifecycleMapping:
    """
    Get lifecycle mapping for a probe category.

    Args:
        category: Probe category name.

    Returns:
        LifecycleMapping with phase information.

    Example:
        >>> mapping = get_category_lifecycle_mapping("prompt_injection")
        >>> mapping.owasp_category
        'LLM01'

    """
    category_lower = category.lower()

    if category_lower not in CATEGORY_TO_LIFECYCLE:
        return LifecycleMapping(
            category=category,
            primary_phase="execution_analysis",
            secondary_phases=["reporting_remediation"],
            owasp_category="UNKNOWN",
        )

    info = CATEGORY_TO_LIFECYCLE[category_lower]

    return LifecycleMapping(
        category=category,
        primary_phase=info["primary_phase"],
        secondary_phases=info["secondary_phases"],
        owasp_category=info["owasp"],
    )


@beartype
def get_owasp_category(category: str) -> str:
    """
    Get OWASP LLM Top 10 category for a probe category.

    Args:
        category: Probe category name.

    Returns:
        OWASP LLM Top 10 category identifier.

    Example:
        >>> get_owasp_category("prompt_injection")
        'LLM01'

    """
    mapping = get_category_lifecycle_mapping(category)
    return mapping.owasp_category


@beartype
def print_lifecycle_overview() -> None:
    """Print an overview of the CPH Sec AI Red Team Lifecycle."""
    print_section_header("CPH Sec AI Red Team Lifecycle", level=1)

    for phase_id, phase_info in LIFECYCLE_PHASES.items():
        console.print(f"\n[bold cyan]{phase_info['name']}[/bold cyan]")
        console.print(f"[dim]Phase: {phase_id}[/dim]")
        console.print(f"\n{phase_info['description']}\n")

        console.print("[bold]Activities:[/bold]")
        for activity in phase_info["activities"]:
            console.print(f"  - {activity}")


@beartype
def print_category_mapping(category: str) -> None:
    """
    Print lifecycle mapping for a specific category.

    Args:
        category: Probe category name.

    """
    mapping = get_category_lifecycle_mapping(category)
    primary_phase = get_lifecycle_phase(mapping.primary_phase)

    console.print(f"\n[bold cyan]{category.upper()}[/bold cyan]")
    console.print(f"OWASP Category: {mapping.owasp_category}")
    console.print(f"\nPrimary Phase: {primary_phase['name']}")
    console.print(f"  {primary_phase['description']}")

    if mapping.secondary_phases:
        console.print("\nSecondary Phases:")
        for phase_id in mapping.secondary_phases:
            phase = get_lifecycle_phase(phase_id)
            console.print(f"  - {phase['name']}")


@beartype
def create_lifecycle_table() -> Table:
    """
    Create a rich table showing lifecycle phases.

    Returns:
        Rich Table object with lifecycle information.

    """
    table = Table(title="CPH Sec AI Red Team Lifecycle", show_header=True)
    table.add_column("Phase", style="cyan", width=30)
    table.add_column("Description", style="white", width=40)
    table.add_column("Key Activities", style="yellow", width=30)

    for phase_info in LIFECYCLE_PHASES.values():
        activities = "\n".join([f"  - {a}" for a in phase_info["activities"][:3]])
        table.add_row(
            phase_info["name"],
            phase_info["description"],
            activities,
        )

    return table


@beartype
def create_owasp_mapping_table() -> Table:
    """
    Create a rich table showing OWASP LLM Top 10 mapping.

    Returns:
        Rich Table object with OWASP mappings.

    """
    table = Table(title="OWASP LLM Top 10 Mapping", show_header=True)
    table.add_column("Probe Category", style="cyan", width=20)
    table.add_column("OWASP Category", style="green", width=10)
    table.add_column("Primary Phase", style="yellow", width=25)
    table.add_column("Description", style="white", width=40)

    for category, mapping in CATEGORY_TO_LIFECYCLE.items():
        phase = get_lifecycle_phase(mapping["primary_phase"])
        table.add_row(
            category.title(),
            mapping["owasp"],
            phase["name"],
            mapping.get("description", ""),
        )

    return table


@beartype
def get_phase_activities(phase_id: str) -> list[str]:
    """
    Get activities for a specific lifecycle phase.

    Args:
        phase_id: Phase identifier.

    Returns:
        List of activities for the phase.

    Example:
        >>> activities = get_phase_activities("planning_reconnaissance")
        >>> "Identify" in activities[0]
        True

    """
    phase = get_lifecycle_phase(phase_id)
    return phase["activities"].copy()


@beartype
def get_remediation_guidance(category: str, severity: str = "MEDIUM") -> dict[str, str]:
    """
    Get remediation guidance for a probe category.

    Args:
        category: Probe category name.
        severity: Severity level (HIGH, MEDIUM, LOW).

    Returns:
        Dictionary with remediation guidance.

    Example:
        >>> guidance = get_remediation_guidance("prompt_injection")
        >>> "immediate" in guidance.values() or "recommended" in guidance.values()
        True

    """
    guidance_map = {
        "prompt_injection": {
            "HIGH": "Implement robust input validation and sanitization immediately",
            "MEDIUM": "Add prompt injection detection and response filtering",
            "LOW": "Monitor for injection patterns and update prompts regularly",
        },
        "jailbreaks": {
            "HIGH": "Implement comprehensive safety guardrails and refusal training",
            "MEDIUM": "Add jailbreak detection and secondary model review",
            "LOW": "Regular safety audits and red team exercises",
        },
        "data_leakage": {
            "HIGH": "Review training data and implement differential privacy",
            "MEDIUM": "Add output filtering for sensitive data patterns",
            "LOW": "Monitor for data leakage and implement data sanitization",
        },
        "malicious_content": {
            "HIGH": "Implement multi-layer content filtering and safety checks",
            "MEDIUM": "Add harmful content detection and blocking",
            "LOW": "Regular safety audits and adversarial testing",
        },
    }

    category_lower = category.lower()

    if category_lower not in guidance_map:
        return {
            "immediate": "Review findings and implement appropriate safeguards",
            "recommended": "Conduct further analysis and testing",
            "optional": "Monitor for related vulnerabilities",
        }

    severity_upper = severity.upper()

    if severity_upper not in ("HIGH", "MEDIUM", "LOW"):
        severity_upper = "MEDIUM"

    return {
        "immediate": guidance_map[category_lower][severity_upper],
        "recommended": "Document findings and track remediation progress",
        "optional": "Share learnings with security team",
    }
