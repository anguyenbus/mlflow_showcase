"""
Python assertion helpers for promptfoo evaluation.

This module provides domain-specific assertion helpers that can be
used in promptfoo evaluations via Python assertions.
"""

import re
from collections.abc import Callable
from typing import Any, Final

from beartype import beartype


@beartype
def contains_tax_keywords(output: str) -> dict[str, Any]:
    """
    Check if output contains tax-related keywords.

    Args:
        output: The text to check.

    Returns:
        Dict with pass (bool), score (float), and reason (str).

    """
    tax_keywords = [
        "tax",
        "income",
        "deduction",
        "gst",
        "refund",
        "assessment",
        "liable",
        "taxable",
        "rates",
    ]

    output_lower = output.lower()
    found_keywords = [kw for kw in tax_keywords if kw in output_lower]

    if not found_keywords:
        return {"pass": False, "score": 0.0, "reason": "No tax-related keywords found in output"}

    score = min(len(found_keywords) / 3, 1.0)  # Cap at 1.0
    return {
        "pass": True,
        "score": score,
        "reason": f"Found tax keywords: {', '.join(found_keywords[:3])}",
    }


@beartype
def contains_australian_currency(output: str) -> dict[str, Any]:
    """
    Check if output contains Australian currency format.

    Args:
        output: The text to check.

    Returns:
        Dict with pass, score, and reason.

    """
    # Match patterns like $100, $1,000, $10.50
    currency_pattern = r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?"
    matches = re.findall(currency_pattern, output)

    if not matches:
        return {
            "pass": False,
            "score": 0.0,
            "reason": "No Australian currency format found (e.g., $100)",
        }

    return {"pass": True, "score": 1.0, "reason": f"Found {len(matches)} currency value(s)"}


@beartype
def mentions_tax_rate(output: str) -> dict[str, Any]:
    """
    Check if output mentions specific tax rates.

    Args:
        output: The text to check.

    Returns:
        Dict with pass, score, and reason.

    """
    # Look for percentage patterns that could be tax rates
    rate_patterns = [
        r"0%",
        r"19%",
        r"32\.5%",
        r"37%",
        r"45%",
        r"10%",
    ]

    found_rates = []
    for pattern in rate_patterns:
        if re.search(pattern, output):
            found_rates.append(pattern)

    if not found_rates:
        return {"pass": False, "score": 0.0, "reason": "No tax rates mentioned"}

    score = min(len(found_rates) / 2, 1.0)
    return {"pass": True, "score": score, "reason": f"Found tax rates: {', '.join(found_rates)}"}


@beartype
def validate_tax_reference(output: str, context: dict[str, Any]) -> dict[str, Any]:
    """
    Validate that output references tax law correctly.

    Args:
        output: The text to check.
        context: Context with expected reference.

    Returns:
        Dict with pass, score, and reason.

    """
    expected_reference = context.get("vars", {}).get("reference", "")

    if not expected_reference:
        return {"pass": True, "score": 1.0, "reason": "No reference required"}

    if expected_reference.lower() in output.lower():
        return {"pass": True, "score": 1.0, "reason": f"Correctly referenced: {expected_reference}"}

    return {"pass": False, "score": 0.0, "reason": f"Missing reference to: {expected_reference}"}


@beartype
def check_answer_relevance(output: str, context: dict[str, Any]) -> dict[str, Any]:
    """
    Check if answer is relevant to the question.

    Args:
        output: The answer text.
        context: Context with question in vars.

    Returns:
        Dict with pass, score, and reason.

    """
    question = context.get("vars", {}).get("question", "")

    if not question:
        return {"pass": True, "score": 1.0, "reason": "No question provided for relevance check"}

    # Simple relevance check: question keywords should appear in answer
    question_words = set(re.findall(r"\b\w+\b", question.lower()))
    # Filter out common words
    # NOTE: List split across lines to satisfy E501 line length
    stop_words = {
        "what",
        "is",
        "the",
        "a",
        "an",
        "in",
        "to",
        "for",
        "of",
        "and",
        "or",
        "but",
        "not",
        "yes",
        "no",
    }
    keywords = question_words - stop_words

    output_lower = output.lower()
    matched_keywords = [kw for kw in keywords if kw in output_lower]

    if not keywords:
        return {"pass": True, "score": 1.0, "reason": "Could not determine relevance (no keywords)"}

    relevance_score = len(matched_keywords) / len(keywords)

    if relevance_score >= 0.5:
        return {
            "pass": True,
            "score": relevance_score,
            "reason": f"Answer appears relevant ({len(matched_keywords)}/{len(keywords)} keywords)",
        }

    return {
        "pass": False,
        "score": relevance_score,
        # NOTE: Split long line to satisfy E501
        "reason": (
            f"Answer may not be relevant ({len(matched_keywords)}/{len(keywords)} keywords matched)"
        ),
    }


@beartype
def validate_context_faithfulness(output: str, context: dict[str, Any]) -> dict[str, Any]:
    """
    Validate that answer is faithful to provided context.

    Args:
        output: The answer text.
        context: Context with retrieved context.

    Returns:
        Dict with pass, score, and reason.

    """
    provided_context = context.get("context", "")

    if not provided_context:
        return {"pass": True, "score": 1.0, "reason": "No context provided for faithfulness check"}

    # Check if output introduces information not in context
    # This is a simple heuristic - real faithfulness requires LLM grading
    output_words = set(re.findall(r"\b\w+\b", output.lower()))
    context_words = set(re.findall(r"\b\w+\b", provided_context.lower()))

    # Remove common words
    # NOTE: List split across lines to satisfy E501 line length
    stop_words = {
        "is",
        "the",
        "a",
        "an",
        "in",
        "to",
        "for",
        "of",
        "and",
        "or",
        "but",
        "not",
        "yes",
        "no",
    }
    output_keywords = output_words - stop_words
    context_keywords = context_words - stop_words

    # Words in output but not in context
    extra_words = output_keywords - context_keywords

    # Allow some extra words (connective phrases, etc.)
    faithfulness_score = 1.0 - min(len(extra_words) / 20, 1.0)

    if faithfulness_score >= 0.7:
        return {
            "pass": True,
            "score": faithfulness_score,
            "reason": "Answer appears faithful to context",
        }

    return {
        "pass": False,
        "score": faithfulness_score,
        "reason": f"Answer may contain information not in context ({len(extra_words)} extra words)",
    }


# Assertion registry for easy access
ASSERTIONS: Final[dict[str, Callable]] = {
    "contains_tax_keywords": contains_tax_keywords,
    "contains_australian_currency": contains_australian_currency,
    "mentions_tax_rate": mentions_tax_rate,
    "validate_tax_reference": validate_tax_reference,
    "check_answer_relevance": check_answer_relevance,
    "validate_context_faithfulness": validate_context_faithfulness,
}


@beartype
def get_assertion(name: str) -> Callable[..., Any] | None:
    """
    Get an assertion function by name.

    Args:
        name: Name of the assertion function.

    Returns:
        The assertion function or None if not found.

    """
    return ASSERTIONS.get(name)
