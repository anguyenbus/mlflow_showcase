"""
Custom promptfoo provider example.

This module demonstrates how to create a custom Python provider for promptfoo
that integrates with external systems or adds custom functionality.
"""

import sys
from pathlib import Path
from typing import Any

from beartype import beartype

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from promptfoo_evaluation.shared.assertions.python_asserts import (
    contains_australian_currency,
    contains_tax_keywords,
    mentions_tax_rate,
)


@beartype
class CustomTaxAssertionProvider:
    """
    Custom provider for tax domain assertions.

    This provider demonstrates the promptfoo provider pattern for
    domain-specific validation and assertion logic.

    Attributes:
        name: Provider name.
        assertions: Available assertion functions.

    Example:
        >>> provider = CustomTaxAssertionProvider()
        >>> result = provider.evaluate(
        ...     prompt="What is tax?",
        ...     output="Tax is a financial obligation..."
        ... )
        >>> print(result["pass"])

    """

    __slots__ = ("name", "assertions")

    def __init__(self) -> None:
        """Initialize the custom provider."""
        self.name = "tax_assertions"
        self.assertions = {
            "contains_tax_keywords": contains_tax_keywords,
            "contains_australian_currency": contains_australian_currency,
            "mentions_tax_rate": mentions_tax_rate,
        }

    def evaluate(
        self,
        prompt: str,
        output: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Evaluate an assertion against LLM output.

        Args:
            prompt: The prompt that was used.
            output: The LLM's output.
            context: Optional context for evaluation.

        Returns:
            Result dict with pass, score, and reason.

        """
        if context is None:
            context = {}

        # Default: check for tax keywords
        assertion_func = self.assertions.get("contains_tax_keywords")
        if assertion_func:
            return assertion_func(output)

        return {"pass": True, "score": 1.0, "reason": "No assertion specified"}

    def call_api(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """
        Simulate an API call (for demonstration).

        In a real custom provider, this would call an external API
        or perform some custom computation.

        Args:
            prompt: The prompt to process.
            context: Optional context for the call.

        Returns:
            The generated response.

        """
        # This is a placeholder - in real use, you might call
        # an external tax API, database, or other service
        return f"Custom provider response for: {prompt[:50]}..."


@beartype
def get_assertion_output(
    prompt: str,
    context: dict[str, Any],
) -> dict[str, Any]:
    """
    Get assertion output for promptfoo integration.

    This is the entry point that promptfoo calls for custom assertions.

    Args:
        prompt: The assertion prompt.
        context: Context dict with output, vars, and other data.

    Returns:
        Assertion result dict.

    Example:
        >>> result = get_assertion_output(
        ...     prompt="Tax keyword check",
        ...     context={"output": "Tax deduction example"}
        ... )
        >>> assert result["pass"] == True

    """
    output = context.get("output", "")
    provider = CustomTaxAssertionProvider()

    # Route to appropriate assertion based on prompt
    if "keyword" in prompt.lower():
        return provider.assertions["contains_tax_keywords"](output)
    elif "currency" in prompt.lower():
        return provider.assertions["contains_australian_currency"](output)
    elif "rate" in prompt.lower():
        return provider.assertions["mentions_tax_rate"](output)
    else:
        # Default: tax keyword check
        return provider.assertions["contains_tax_keywords"](output)


# Allow running as standalone script for testing
if __name__ == "__main__":
    # Test the provider
    provider = CustomTaxAssertionProvider()

    test_cases = [
        "Income tax is calculated on assessable income minus deductions.",
        "The GST rate is 10% in Australia.",
        "You can claim work-related expenses as tax deductions.",
        "This is a generic response with no tax content.",
    ]

    print("Custom Tax Assertion Provider Tests")
    print("=" * 50)

    for i, test_output in enumerate(test_cases, 1):
        result = provider.evaluate(prompt="Tax assertion test", output=test_output)
        print(f"\nTest {i}: {test_output[:50]}...")
        print(f"  Pass: {result['pass']}")
        print(f"  Score: {result.get('score', 'N/A')}")
        print(f"  Reason: {result['reason']}")
