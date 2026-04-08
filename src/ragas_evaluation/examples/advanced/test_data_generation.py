"""
Test Data Generation Example.

This script demonstrates generating test data for RAGas evaluation.

Shows:
1. Synthetic test data generation using RAGAS TestsetGenerator
2. Golden dataset creation from existing documents
3. Data quality validation checks
4. Reproducibility patterns (random seeds)

Expected Output:
    Test Data Generation Example
    ============================

    Generating Synthetic Dataset
    Created 5 synthetic test samples

    Creating Golden Dataset
    Created 3 golden dataset samples

    Validating Dataset Quality
    Validation passed: 8/8 samples valid

    Exporting Dataset
    Exported 8 samples to JSON format
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from beartype import beartype
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Initialize rich console for output
console: Final[Console] = Console()


@beartype
@dataclass(frozen=True, slots=True)
class DatasetStats:
    """Statistics about a generated dataset.

    Attributes:
        total_samples: Total number of samples
        valid_samples: Number of valid samples
        avg_question_length: Average question length
        avg_context_count: Average number of contexts per sample

    """

    total_samples: int
    valid_samples: int
    avg_question_length: float
    avg_context_count: float


@beartype
def generate_synthetic_dataset(
    num_samples: int,
    document_corpus: list[str],
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Generate synthetic test dataset from documents.

    Args:
        num_samples: Number of samples to generate
        document_corpus: List of documents to use for generation
        seed: Random seed for reproducibility

    Returns:
        List of synthetic test samples

    """
    import random

    console.print(f"\n[cyan]Generating Synthetic Dataset[/cyan]")
    console.print(f"  Samples: {num_samples}")
    console.print(f"  Documents: {len(document_corpus)}")
    console.print(f"  Seed: {seed}")

    random.seed(seed)

    dataset = []

    # NOTE: In production, use RAGAS TestsetGenerator
    # For demonstration, we create simple synthetic samples
    for i in range(num_samples):
        # Select random document
        doc = random.choice(document_corpus)

        # Generate question based on document
        question = f"Sample question {i + 1} about: {doc[:50]}..."

        # Use document as context
        contexts = [doc]

        # Generate simple response
        response = f"Based on the context, {doc[:100]}..."

        dataset.append({
            "question": question,
            "contexts": contexts,
            "response": response,
            "reference_answer": doc,  # Use document as reference
        })

    console.print(f"  [green]Created {len(dataset)} synthetic samples[/green]")

    return dataset


@beartype
def create_golden_dataset(
    documents: list[dict[str, Any]],
    questions_per_doc: int = 2,
) -> list[dict[str, Any]]:
    """Create golden dataset from existing documents.

    Args:
        documents: List of documents with content and metadata
        questions_per_doc: Number of questions to generate per document

    Returns:
        List of golden dataset samples

    """
    console.print(f"\n[cyan]Creating Golden Dataset[/cyan]")
    console.print(f"  Documents: {len(documents)}")
    console.print(f"  Questions per document: {questions_per_doc}")

    dataset = []

    for doc in documents:
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})

        # Generate questions from document
        for i in range(questions_per_doc):
            question = f"What information is contained in this document about {content[:30]}...?"

            # Create response based on content
            response = f"{content[:200]}..."

            dataset.append({
                "question": question,
                "contexts": [content],
                "response": response,
                "reference_answer": content,
                "metadata": metadata,
            })

    console.print(f"  [green]Created {len(dataset)} golden samples[/green]")

    return dataset


@beartype
def validate_dataset_quality(dataset: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate dataset quality with various checks.

    Args:
        dataset: Dataset to validate

    Returns:
        Dictionary with validation results

    """
    console.print(f"\n[cyan]Validating Dataset Quality[/cyan]")

    errors = []
    valid_count = 0

    for idx, sample in enumerate(dataset):
        # Check required fields
        if "question" not in sample:
            errors.append(f"Sample {idx}: missing 'question'")
            continue

        if "contexts" not in sample:
            errors.append(f"Sample {idx}: missing 'contexts'")
            continue

        if "response" not in sample:
            errors.append(f"Sample {idx}: missing 'response'")
            continue

        # Check question relevance (basic check)
        if len(sample["question"]) < 10:
            errors.append(f"Sample {idx}: question too short")

        # Check contexts not empty
        if not sample["contexts"] or len(sample["contexts"]) == 0:
            errors.append(f"Sample {idx}: contexts is empty")
            continue

        # Check response not empty
        if not sample["response"] or len(sample["response"]) < 5:
            errors.append(f"Sample {idx}: response too short")
            continue

        valid_count += 1

    result = {
        "valid": len(errors) == 0,
        "total": len(dataset),
        "valid_count": valid_count,
        "errors": errors,
    }

    status = "[green]PASSED[/green]" if result["valid"] else "[red]FAILED[/red]"
    console.print(f"  Validation {status}: {valid_count}/{len(dataset)} samples valid")

    if errors:
        console.print(f"  [yellow]Errors found:[/yellow]")
        for error in errors[:5]:  # Show first 5 errors
            console.print(f"    - {error}")
        if len(errors) > 5:
            console.print(f"    ... and {len(errors) - 5} more errors")

    return result


@beartype
def export_dataset_to_json(
    dataset: list[dict[str, Any]],
    output_path: Path | None = None,
) -> str:
    """Export dataset to RAGAS-compatible JSON format.

    Args:
        dataset: Dataset to export
        output_path: Optional path to save JSON file

    Returns:
        JSON string of the dataset

    """
    console.print(f"\n[cyan]Exporting Dataset[/cyan]")

    # Convert to JSON
    json_str = json.dumps(dataset, indent=2)

    # Save to file if path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(json_str)
        console.print(f"  [green]Saved to:[/green] {output_path}")

    console.print(f"  [green]Exported {len(dataset)} samples to JSON[/green]")

    return json_str


@beartype
def calculate_dataset_statistics(dataset: list[dict[str, Any]]) -> DatasetStats:
    """Calculate statistics about a dataset.

    Args:
        dataset: Dataset to analyze

    Returns:
        DatasetStats with calculated statistics

    """
    total_samples = len(dataset)

    # Calculate averages
    question_lengths = [len(s.get("question", "")) for s in dataset]
    avg_question_length = sum(question_lengths) / len(question_lengths) if question_lengths else 0

    context_counts = [len(s.get("contexts", [])) for s in dataset]
    avg_context_count = sum(context_counts) / len(context_counts) if context_counts else 0

    return DatasetStats(
        total_samples=total_samples,
        valid_samples=total_samples,  # Assume valid if in dataset
        avg_question_length=avg_question_length,
        avg_context_count=avg_context_count,
    )


@beartype
def display_reproducibility_guidance() -> None:
    """Display guidance on dataset reproducibility."""
    guidance = Panel(
        "[bold yellow]Reproducibility Best Practices:[/bold yellow]\n\n"
        "• [green]Random Seeds:[/green]\n"
        "  - Always set random seed for synthetic generation\n"
        "  - Document seed in dataset metadata\n"
        "  - Use consistent seeds across experiments\n\n"
        "• [cyan]Dataset Versioning:[/cyan]\n"
        "  - Version your datasets (v1.0, v1.1, etc.)\n"
        "  - Track changes and updates\n"
        "  - Store golden datasets separately from synthetic\n\n"
        "• [blue]Size Considerations:[/blue]\n"
        "  - Minimum viable size: 50-100 samples\n"
        "  - Statistical significance: 200+ samples\n"
        "  - Balance quality vs quantity\n\n"
        "• [magenta]Storage Patterns:[/magenta]\n"
        "  - Use JSON for portability\n"
        "  - Include metadata (creation date, seed, version)\n"
        "  - Separate train/validation/test splits",
        title="[bold cyan]Reproducibility Guidance[/bold cyan]",
        border_style="cyan",
    )
    console.print(guidance)


@beartype
def main() -> None:
    """Run test data generation example.

    Demonstrates:
    1. Synthetic data generation
    2. Golden dataset creation
    3. Data quality validation
    4. Reproducibility patterns
    """
    # Header
    console.print(
        Panel(
            "[bold cyan]Test Data Generation Example[/bold cyan]\n"
            "Demonstrating synthetic and golden dataset generation for RAG evaluation",
            title="[bold green]RAGas Advanced Example[/bold green]",
            border_style="cyan",
        )
    )

    # Sample document corpus
    document_corpus = [
        "GST is a broad-based tax of 10% on most goods and services in Australia.",
        "Income tax rates for 2024-25 range from 0% to 45% depending on income level.",
        "Work-related expenses can be claimed as tax deductions if directly related to earning income.",
        "A Tax File Number (TFN) is required for tax purposes and to avoid high withholding rates.",
        "Capital gains tax applies to profits from selling assets like property or shares.",
    ]

    # 1. Generate synthetic dataset
    console.print("\n[bold yellow]1. Synthetic Data Generation[/bold yellow]")
    synthetic_dataset = generate_synthetic_dataset(
        num_samples=5,
        document_corpus=document_corpus,
        seed=42,  # For reproducibility
    )

    # 2. Create golden dataset
    console.print("\n[bold yellow]2. Golden Dataset Creation[/bold yellow]")
    documents = [
        {"content": doc, "metadata": {"source": f"doc_{i}.pdf"}}
        for i, doc in enumerate(document_corpus[:3])
    ]
    golden_dataset = create_golden_dataset(documents=documents, questions_per_doc=1)

    # 3. Combine datasets
    combined_dataset = synthetic_dataset + golden_dataset

    # 4. Validate quality
    console.print("\n[bold yellow]3. Data Quality Validation[/bold yellow]")
    validation_result = validate_dataset_quality(combined_dataset)

    # 5. Calculate statistics
    stats = calculate_dataset_statistics(combined_dataset)

    # Display statistics
    console.print(f"\n[cyan]Dataset Statistics:[/cyan]")
    console.print(f"  Total samples: {stats.total_samples}")
    console.print(f"  Valid samples: {stats.valid_samples}")
    console.print(f"  Avg question length: {stats.avg_question_length:.1f} chars")
    console.print(f"  Avg context count: {stats.avg_context_count:.1f}")

    # 6. Display sample comparison
    console.print("\n[bold yellow]4. Dataset Comparison[/bold yellow]")

    table = Table(title="Synthetic vs Golden Datasets")
    table.add_column("Type", style="cyan", width=15)
    table.add_column("Use Case", style="green", width=30)
    table.add_column("Pros", style="yellow", width=30)

    table.add_row(
        "Synthetic",
        "Development, testing, rapid iteration",
        "Fast to generate, controlled variety",
    )
    table.add_row(
        "Golden",
        "Production evaluation, benchmarking",
        "Realistic, human-validated quality",
    )

    console.print(table)

    # Display reproducibility guidance
    console.print("\n")
    display_reproducibility_guidance()

    # Summary
    summary_text = Text.from_markup(
        f"[bold green]Data Generation Summary[/bold green]\n"
        f"• Synthetic samples: {len(synthetic_dataset)}\n"
        f"• Golden samples: {len(golden_dataset)}\n"
        f"• Total samples: {len(combined_dataset)}\n"
        f"• Validation: {'PASSED' if validation_result['valid'] else 'FAILED'}\n"
        f"[dim]Key insight: Combine synthetic and golden data for comprehensive evaluation[/dim]"
    )
    console.print(Panel(summary_text, title="[bold cyan]Generation Complete[/bold cyan]", border_style="cyan"))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")
        raise
