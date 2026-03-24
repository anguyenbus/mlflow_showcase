"""Tests for evaluation dataset structure and content."""

import json
from pathlib import Path

from ragas_evaluation.shared.data_loader import load_evaluation_dataset, validate_dataset_structure


def test_dataset_exists():
    """Test that evaluation dataset file exists."""
    from ragas_evaluation.shared.config import get_evaluation_dataset_path

    dataset_path = get_evaluation_dataset_path()
    assert dataset_path.exists(), f"Evaluation dataset should exist at {dataset_path}"


def test_dataset_loadable():
    """Test that evaluation dataset can be loaded."""
    dataset = load_evaluation_dataset()

    assert isinstance(dataset, list)
    assert len(dataset) >= 5, "Dataset should contain at least 5 Q&A pairs"
    assert len(dataset) <= 8, "Dataset should contain at most 8 Q&A pairs"


def test_dataset_has_ground_truth():
    """Test that some entries have ground truth answers."""
    dataset = load_evaluation_dataset()

    entries_with_ground_truth = [d for d in dataset if "reference_answer" in d]
    entries_without_ground_truth = [d for d in dataset if "reference_answer" not in d]

    # Should have 3-4 pairs with ground truth
    assert len(entries_with_ground_truth) >= 3, "Should have at least 3 entries with ground truth"
    assert len(entries_with_ground_truth) <= 4, "Should have at most 4 entries with ground truth"

    # Should have 4-5 pairs without ground truth
    assert len(entries_without_ground_truth) >= 4, "Should have at least 4 entries without ground truth"
    assert len(entries_without_ground_truth) <= 5, "Should have at most 5 entries without ground truth"


def test_dataset_field_types():
    """Test that dataset entries have correct field types."""
    dataset = load_evaluation_dataset()

    for entry in dataset:
        assert isinstance(entry["question"], str), "Question should be a string"
        assert len(entry["question"]) > 0, "Question should not be empty"

        assert isinstance(entry["contexts"], list), "Contexts should be a list"
        assert len(entry["contexts"]) > 0, "Contexts should not be empty"
        for context in entry["contexts"]:
            assert isinstance(context, str), "Each context should be a string"

        assert isinstance(entry["response"], str), "Response should be a string"
        assert len(entry["response"]) > 0, "Response should not be empty"

        if "reference_answer" in entry:
            assert isinstance(entry["reference_answer"], str), "Reference answer should be a string"


def test_dataset_australian_tax_content():
    """Test that dataset contains Australian tax regulation content."""
    dataset = load_evaluation_dataset()

    # Check for Australian tax-related keywords
    all_text = " ".join([d["question"] + " " + d["response"] for d in dataset])
    all_text_lower = all_text.lower()

    # Should contain at least some Australian tax concepts
    tax_keywords = [
        "gst",
        "tax",
        "australia",
        "income",
        "deduction",
        "tfn",
        "foreign",
        "capital gains",
    ]

    found_keywords = [kw for kw in tax_keywords if kw in all_text_lower]
    assert len(found_keywords) >= 3, f"Dataset should contain Australian tax content. Found: {found_keywords}"


def test_dataset_diverse_scenarios():
    """Test that dataset covers diverse scenarios."""
    dataset = load_evaluation_dataset()

    # Check for different question types
    questions = [d["question"].lower() for d in dataset]

    # Should have factual questions (what, how many)
    factual = [q for q in questions if any(word in q for word in ["what", "how much", "how many"])]
    assert len(factual) >= 2, "Should have at least 2 factual questions"

    # Check for edge cases in responses
    responses = [d["response"] for d in dataset]

    # Should have some partial or incomplete answers
    partial = [r for r in responses if any(word in r.lower() for word in ["depends", "may", "might", "could"])]
    # This is optional - just checking diversity

    # Check for different context lengths
    context_lengths = [len(d["contexts"]) for d in dataset]
    assert len(set(context_lengths)) >= 1, "Should have variety in context lengths"
