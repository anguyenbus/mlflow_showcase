"""
Probe management utilities for Garak evaluation tutorials.

This module provides utilities for probe selection, CLI argument
building, and YAML configuration generation for Garak evaluations.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import yaml
from beartype import beartype

# NOTE: Import console_output utilities
from garak_evaluation.shared.console_output import console, print_section_header

# Garak probe categories mapped to OWASP LLM Top 10
PROBE_CATEGORIES: Final[dict[str, dict[str, Any]]] = {
    "prompt_injection": {
        "probes": [
            "blake.AvalancheInjection",
            "blake.Injector",
            "gcg.GCGConfig",
            "encoding.B64NestedInjection",
            "encoding.MorseInjection",
            "encoding.UnicodeConfusable",
            "web_injection.DirectIndirectInjection",
            "web_injection.JailbreakInHTML",
            "latentinjection.LatentInjection",
            "latentinjection.LatentInjectionJSON",
        ],
        "owasp": "LLM01",
        "description": "Direct and indirect prompt injection attacks",
    },
    "jailbreaks": {
        "probes": [
            "dan.DAN",
            "dan.DAN2023",
            "grandma.Grandma",
            "goodside.Goodside",
            "jailbreak.ChatGPTJailbreak",
            "jailbreak.JailbreakChatGPT",
            "payloadanalyzer.PayloadAnalyzer",
        ],
        "owasp": "LLM01",
        "description": "Jailbreak attempts to bypass safety guardrails",
    },
    "data_leakage": {
        "probes": [
            "replay.Replay",
            "replay.PromptExtraction",
            "knownbadsignatures.KnownBadSignatures",
            "hallucination.Hallucination",
            "leakage.Leakage",
        ],
        "owasp": "LLM06",
        "description": "Training data extraction and sensitive information leakage",
    },
    "malicious_content": {
        "probes": [
            "malwaregen.MalwareGen",
            "malwaregen.PackageHallucination",
            "knownbadsignatures.KnownBadSignatures",
            "harmful.HarmfulContent",
            "atkgen.ATKGen",
        ],
        "owasp": "LLM03",
        "description": "Malicious code generation and harmful content",
    },
}


@beartype
@dataclass(frozen=True, slots=True)
class ProbeConfig:
    """
    Configuration for a Garak probe run.

    Attributes:
        probe_name: Name of the probe to run.
        detector_type: Type of detector to use.
        model_name: Name of the model to evaluate.
        generators: List of generator configurations.

    """

    probe_name: str
    detector_type: str
    model_name: str
    generators: list[dict[str, Any]]


@beartype
def get_available_probes(category: str) -> list[str]:
    """
    Get available probes for a given category.

    Args:
        category: Probe category (prompt_injection, jailbreaks, etc.).

    Returns:
        List of probe names for the category.

    Raises:
        ValueError: If category is not recognized.

    Example:
        >>> probes = get_available_probes("prompt_injection")
        >>> "blake.AvalancheInjection" in probes
        True

    """
    category_lower = category.lower()

    if category_lower not in PROBE_CATEGORIES:
        available = ", ".join(PROBE_CATEGORIES.keys())
        raise ValueError(
            f"Unknown category: {category}. Available: {available}"
        )

    return PROBE_CATEGORIES[category_lower]["probes"]


@beartype
def get_owasp_mapping(category: str) -> str:
    """
    Get OWASP LLM Top 10 category for a probe category.

    Args:
        category: Probe category.

    Returns:
        OWASP LLM Top 10 category identifier.

    Example:
        >>> get_owasp_mapping("prompt_injection")
        'LLM01'

    """
    category_lower = category.lower()

    if category_lower not in PROBE_CATEGORIES:
        return "UNKNOWN"

    return PROBE_CATEGORIES[category_lower]["owasp"]


@beartype
def build_cli_args(
    probe_names: list[str],
    model_name: str = "glm-5-flash",
    detector_type: str = "all",
    output_file: str | None = None,
) -> list[str]:
    """
    Build CLI arguments for Garak evaluation.

    Args:
        probe_names: List of probe names to run.
        model_name: Name of the model to evaluate.
        detector_type: Type of detector to use.
        output_file: Optional output file path.

    Returns:
        List of CLI argument strings.

    Example:
        >>> args = build_cli_args(["dan.DAN"], "glm-5-flash")
        >>> "garak" in args[0]
        False
        >>> "--probe_type" in args
        True

    """
    args = []

    # Model configuration
    args.extend(["--model_type", "openai-compatible"])
    args.extend(["--model_name", model_name])

    # Base URL for Zhipu AI
    args.extend(["--openai_base", "https://open.bigmodel.cn/api/paas/v4/"])

    # Probes
    for probe in probe_names:
        args.extend(["--probe_type", probe])

    # Detector
    if detector_type:
        args.extend(["--detector_type", detector_type])

    # Output
    if output_file:
        args.extend(["--report_prefix", output_file])

    return args


@beartype
def generate_yaml_config(
    probe_names: list[str],
    model_name: str = "glm-5-flash",
    generator_type: str = "openai-compatible",
    output_path: Path | str | None = None,
) -> dict[str, Any]:
    """
    Generate a YAML configuration for Garak evaluation.

    Args:
        probe_names: List of probe names to include.
        model_name: Name of the model to evaluate.
        generator_type: Type of generator to use.
        output_path: Optional path to save the YAML file.

    Returns:
        Dictionary containing the YAML configuration.

    Example:
        >>> config = generate_yaml_config(["dan.DAN"], "glm-5-flash")
        >>> "generators" in config
        True

    """
    config = {
        "generators": [
            {
                "type": generator_type,
                "name": model_name,
                "api_base": "https://open.bigmodel.cn/api/paas/v4/",
            }
        ],
        "probes": probe_names,
        "detectors": ["all"],
        "report_prefix": "garak_eval",
    }

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)

        console.print(f"[green]YAML config written to:[/green] {output_path}")

    return config


@beartype
def get_category_description(category: str) -> str:
    """
    Get description for a probe category.

    Args:
        category: Probe category.

    Returns:
        Description of the category.

    Example:
        >>> desc = get_category_description("prompt_injection")
        >>> "injection" in desc.lower()
        True

    """
    category_lower = category.lower()

    if category_lower not in PROBE_CATEGORIES:
        return "Unknown category"

    return PROBE_CATEGORIES[category_lower]["description"]


@beartype
def list_all_categories() -> dict[str, dict[str, Any]]:
    """
    List all available probe categories.

    Returns:
        Dictionary of all categories with their metadata.

    Example:
        >>> categories = list_all_categories()
        >>> "prompt_injection" in categories
        True

    """
    return PROBE_CATEGORIES.copy()


@beartype
def print_category_summary() -> None:
    """Print a summary of all available probe categories."""
    print_section_header("Garak Probe Categories", level=2)

    for category, info in PROBE_CATEGORIES.items():
        console.print(f"\n[bold cyan]{category}[/bold cyan]")
        console.print(f"  OWASP: {info['owasp']}")
        console.print(f"  Description: {info['description']}")
        console.print(f"  Probes: {len(info['probes'])} available")


@beartype
def get_recommended_probes(
    category: str,
    max_probes: int | None = None,
) -> list[str]:
    """
    Get recommended probes for a category.

    Args:
        category: Probe category.
        max_probes: Maximum number of probes to return.

    Returns:
        List of recommended probe names.

    Example:
        >>> probes = get_recommended_probes("prompt_injection", 3)
        >>> len(probes) <= 3
        True

    """
    probes = get_available_probes(category)

    # Prioritize commonly used probes
    priority_probes = {
        "prompt_injection": [
            "encoding.B64NestedInjection",
            "web_injection.DirectIndirectInjection",
            "latentinjection.LatentInjection",
        ],
        "jailbreaks": [
            "dan.DAN",
            "grandma.Grandma",
            "goodside.Goodside",
        ],
        "data_leakage": [
            "replay.Replay",
            "hallucination.Hallucination",
            "leakage.Leakage",
        ],
        "malicious_content": [
            "malwaregen.MalwareGen",
            "malwaregen.PackageHallucination",
            "harmful.HarmfulContent",
        ],
    }

    category_lower = category.lower()
    if category_lower in priority_probes:
        recommended = [
            p for p in priority_probes[category_lower] if p in probes
        ] + [p for p in probes if p not in priority_probes[category_lower]]
    else:
        recommended = probes

    if max_probes:
        return recommended[:max_probes]

    return recommended


@beartype
def validate_probe_name(probe_name: str) -> bool:
    """
    Validate if a probe name is known.

    Args:
        probe_name: Name of the probe to validate.

    Returns:
        True if probe is known, False otherwise.

    Example:
        >>> validate_probe_name("dan.DAN")
        True

    """
    for category_info in PROBE_CATEGORIES.values():
        if probe_name in category_info["probes"]:
            return True

    return False
