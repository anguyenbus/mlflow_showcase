"""
Data loading utilities for RAGas evaluation.

This module provides functions for loading and validating
evaluation datasets for RAGas metrics.
"""

import json
from typing import Any, Final

from beartype import beartype
from rich.console import Console

from ragas_evaluation.shared.config import get_evaluation_dataset_path

# Initialize rich console for output
console: Final[Console] = Console()

# Required fields for evaluation dataset
REQUIRED_FIELDS: Final[tuple[str, ...]] = ("question", "contexts", "response")


@beartype
def validate_dataset_structure(data: Any) -> None:
    """
    Validate that the dataset has the correct structure.

    Args:
        data: Dataset to validate

    Raises:
        ValueError: If dataset structure is invalid

    """
    # Check that data is a list
    if not isinstance(data, list):
        raise ValueError("Dataset must be a list of evaluation examples")

    # Check that dataset is not empty
    if len(data) == 0:
        raise ValueError("Dataset cannot be empty")

    # Validate each entry
    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            raise ValueError(f"Entry {i} must be a dictionary")

        # Check required fields
        missing_fields = [field for field in REQUIRED_FIELDS if field not in entry]
        if missing_fields:
            raise ValueError(f"Entry {i} is missing required fields: {', '.join(missing_fields)}")

        # Validate contexts is a list
        if not isinstance(entry["contexts"], list):
            raise ValueError(f"Entry {i}: contexts must be a list")

        # Validate contexts is not empty
        if len(entry["contexts"]) == 0:
            raise ValueError(f"Entry {i}: contexts cannot be empty")

        # Validate reference_answer is present (optional field)
        if "reference_answer" in entry:
            if not isinstance(entry["reference_answer"], str):
                raise ValueError(f"Entry {i}: reference_answer must be a string")


@beartype
def load_evaluation_dataset() -> list[dict[str, Any]]:
    """
    Load the evaluation dataset from JSON file.

    Returns:
        List of dictionaries containing evaluation examples with fields:
        - question: str - The question asked
        - contexts: List[str] - Retrieved context passages
        - response: str - The generated response
        - reference_answer: Optional[str] - Ground truth answer (optional)

    Raises:
        FileNotFoundError: If dataset file doesn't exist
        ValueError: If dataset structure is invalid
        json.JSONDecodeError: If JSON parsing fails

    """
    dataset_path = get_evaluation_dataset_path()

    # Check if file exists
    if not dataset_path.exists():
        console.print(f"[red]ERROR:[/red] Evaluation dataset not found at: {dataset_path}")
        console.print("\n[yellow]To fix:[/yellow]")
        console.print("1. Create the data directory:")
        console.print(f"   mkdir -p {dataset_path.parent}")
        console.print("2. Create evaluation_dataset.json with your test data")
        console.print("3. See documentation for dataset structure examples")
        raise FileNotFoundError(f"Evaluation dataset not found at: {dataset_path}")

    # Load and parse JSON
    console.print(f"[cyan]Loading evaluation dataset from:[/cyan] {dataset_path}")
    try:
        with open(dataset_path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]ERROR:[/red] Invalid JSON in dataset file: {e}")
        raise

    # Validate structure
    try:
        validate_dataset_structure(data)
    except ValueError as e:
        console.print(f"[red]ERROR:[/red] Invalid dataset structure: {e}")
        raise

    console.print(f"[green]✓[/green] Loaded {len(data)} evaluation examples")

    return data
