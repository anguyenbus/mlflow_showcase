"""Tests for Python assertions.

Tests for domain-specific assertion helpers.
"""

from promptfoo_evaluation.shared.assertions.python_asserts import (
    ASSERTIONS,
    check_answer_relevance,
    contains_australian_currency,
    contains_tax_keywords,
    get_assertion,
    mentions_tax_rate,
    validate_context_faithfulness,
    validate_tax_reference,
)


class TestTaxAssertions:
    """Tests for tax domain assertions."""

    def test_contains_tax_keywords_found(self) -> None:
        """Test that tax keywords are detected."""
        output = "Income tax is calculated on assessable income minus deductions."
        result = contains_tax_keywords(output)
        assert result["pass"] is True
        assert result["score"] > 0

    def test_contains_tax_keywords_not_found(self) -> None:
        """Test that missing tax keywords return failure."""
        # NOTE: Using output that has no tax-related words
        output = "This is a random string about blue sky thinking."
        result = contains_tax_keywords(output)
        assert result["pass"] is False
        assert result["score"] == 0.0

    def test_contains_australian_currency_found(self) -> None:
        """Test that Australian currency format is detected."""
        output = "The fee is $100.50 for this service."
        result = contains_australian_currency(output)
        assert result["pass"] is True

    def test_mentions_tax_rate_found(self) -> None:
        """Test that tax rates are detected."""
        output = "The GST rate is 10% and income tax starts at 0%."
        result = mentions_tax_rate(output)
        assert result["pass"] is True
        assert result["score"] > 0

    def test_validate_tax_reference_with_reference(self) -> None:
        """Test validation with expected reference."""
        output = "As per Income Tax Assessment Act 1936..."
        result = validate_tax_reference(
            output, {"vars": {"reference": "Income Tax Assessment Act"}}
        )
        assert result["pass"] is True

    def test_check_answer_relevance_relevant(self) -> None:
        """Test relevant answer scoring."""
        output = "Tax is calculated on assessable income."
        result = check_answer_relevance(output, {"vars": {"question": "How is tax calculated?"}})
        assert result["pass"] is True
        assert "relevant" in result["reason"].lower()

    def test_validate_context_faithfulness_faithful(self) -> None:
        """Test faithful answer validation."""
        output = "Income includes salary and wages."
        result = validate_context_faithfulness(
            output, {"context": "Income includes salary and wages and business income."}
        )
        assert result["pass"] is True


class TestAssertionRegistry:
    """Tests for assertion registry."""

    def test_assertions_registry_contains_all(self) -> None:
        """Test that all expected assertions are registered."""
        expected = {
            "contains_tax_keywords",
            "contains_australian_currency",
            "mentions_tax_rate",
            "validate_tax_reference",
            "check_answer_relevance",
            "validate_context_faithfulness",
        }
        for name in expected:
            assert name in ASSERTIONS
            assert callable(ASSERTIONS[name])

    def test_get_assertion_existing(self) -> None:
        """Test getting existing assertion by name."""
        assertion = get_assertion("contains_tax_keywords")
        assert assertion is not None
        assert callable(assertion)

    def test_get_assertion_nonexistent(self) -> None:
        """Test getting non-existent assertion returns None."""
        assertion = get_assertion("nonexistent_assertion")
        assert assertion is None
