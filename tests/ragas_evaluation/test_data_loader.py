"""Tests for data loader utilities."""

import json
from pathlib import Path
from unittest import mock

import pytest

from ragas_evaluation.shared.data_loader import (
    load_evaluation_dataset,
    validate_dataset_structure,
)


@pytest.fixture
def sample_dataset(tmp_path: Path):
    """Create a sample evaluation dataset for testing."""
    data = [
        {
            "question": "What is the GST rate in Australia?",
            "contexts": ["GST is a broad-based tax of 10% on most goods, services and other items in Australia."],
            "response": "The GST rate in Australia is 10%.",
            "reference_answer": "The GST rate is 10%.",
        },
        {
            "question": "What are the income tax rates for 2024?",
            "contexts": ["The income tax rates for 2024 range from 0% to 45%."],
            "response": "Income tax rates for 2024 range from 0% to 45%.",
        },
    ]

    dataset_path = tmp_path / "evaluation_dataset.json"
    with open(dataset_path, "w") as f:
        json.dump(data, f)

    return dataset_path


def test_load_evaluation_dataset_success(sample_dataset: Path):
    """Test successful loading of evaluation dataset."""
    with mock.patch("ragas_evaluation.shared.data_loader.get_evaluation_dataset_path", return_value=sample_dataset):
        dataset = load_evaluation_dataset()

        assert isinstance(dataset, list)
        assert len(dataset) == 2
        assert dataset[0]["question"] == "What is the GST rate in Australia?"
        assert dataset[1]["question"] == "What are the income tax rates for 2024?"


def test_load_evaluation_dataset_file_not_found():
    """Test loading dataset when file doesn't exist."""
    with mock.patch(
        "ragas_evaluation.shared.data_loader.get_evaluation_dataset_path",
        return_value=Path("/nonexistent/dataset.json"),
    ):
        with pytest.raises(FileNotFoundError, match="Evaluation dataset not found"):
            load_evaluation_dataset()


def test_validate_dataset_structure_valid(sample_dataset: Path):
    """Test validation of valid dataset structure."""
    with open(sample_dataset, "r") as f:
        data = json.load(f)

    # Should not raise any exception
    validate_dataset_structure(data)


def test_validate_dataset_structure_invalid_type():
    """Test validation fails for invalid data type."""
    with pytest.raises(ValueError, match="Dataset must be a list"):
        validate_dataset_structure("not_a_list")


def test_validate_dataset_structure_missing_fields():
    """Test validation fails for missing required fields."""
    invalid_data = [
        {
            "question": "Test question",
            # Missing 'contexts' and 'response' fields
        }
    ]

    with pytest.raises(ValueError, match="missing required fields"):
        validate_dataset_structure(invalid_data)


def test_validate_dataset_structure_invalid_contexts_type():
    """Test validation fails for invalid contexts type."""
    invalid_data = [
        {
            "question": "Test question",
            "contexts": "not_a_list",  # Should be a list
            "response": "Test response",
        }
    ]

    with pytest.raises(ValueError, match="contexts must be a list"):
        validate_dataset_structure(invalid_data)


def test_validate_dataset_structure_empty_dataset():
    """Test validation fails for empty dataset."""
    with pytest.raises(ValueError, match="Dataset cannot be empty"):
        validate_dataset_structure([])
