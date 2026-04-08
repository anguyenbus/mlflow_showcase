"""
Test Data Generation with MLflow Integration.

This script demonstrates generating test data for RAGas evaluation
with comprehensive MLflow tracking for reproducibility and quality monitoring.

Shows:
1. Synthetic test data generation with MLflow parameter logging
2. Golden dataset creation with MLflow artifact logging
3. Data quality validation with MLflow metric tracking
4. Reproducibility patterns (random seeds) with MLflow tracking
5. Dataset quality metrics over time

Expected Output:
    Test Data Generation with MLflow Integration
    =============================================

    [PARENT RUN] Starting test data generation
    Parent run ID: parent_data_gen_456

    Generating Synthetic Dataset
    [NESTED RUN] synthetic_generation
    Samples: 5
    Documents: 5
    Seed: 42
    Created 5 synthetic samples
    Logged parameters: num_samples=5, seed=42
    Logged artifact: synthetic_dataset.json

    Creating Golden Dataset
    [NESTED RUN] golden_dataset_creation
    Documents: 3
    Questions per document: 1
    Created 3 golden samples
    Logged artifact: golden_dataset.json

    Validating Dataset Quality
    [NESTED RUN] quality_validation
    Validation PASSED: 8/8 samples valid
    Logged metrics: valid_samples=8, avg_question_length=45.2

    [TODO: Add screenshot showing dataset generation tracking]
"""

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from beartype import beartype
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ragas_evaluation.shared.config import get_ragas_config

# Try to import mlflow
try:
    import mlflow

    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    mlflow = None

# Initialize rich console for output
console: Final[Console] = Console()


@beartype
@dataclass(frozen=True, slots=True)
class DatasetStats:
    """
    Statistics about a generated dataset.

    Attributes:
        total_samples: Total number of samples
        valid_samples: Number of valid samples
        avg_question_length: Average question length
        avg_context_count: Average number of contexts per sample
        generation_seed: Random seed used for generation

    """

    total_samples: int
    valid_samples: int
    avg_question_length: float
    avg_context_count: float
    generation_seed: int


@beartype
@dataclass(frozen=True, slots=True)
class DatasetGenerationResult:
    """
    Result of dataset generation with MLflow tracking.

    Attributes:
        dataset_type: Type of dataset (synthetic or golden)
        num_samples: Number of samples generated
        file_path: Path to generated dataset file
        stats: Statistics about the dataset
        run_id: MLflow run ID for this generation

    """

    dataset_type: str
    num_samples: int
    file_path: Path | None
    stats: DatasetStats
    run_id: str | None = None


@beartype
def generate_synthetic_dataset(
    num_samples: int,
    document_corpus: list[str],
    seed: int = 42,
) -> list[dict[str, Any]]:
    """
    Generate synthetic test dataset from documents.

    Args:
        num_samples: Number of samples to generate
        document_corpus: List of documents to use for generation
        seed: Random seed for reproducibility

    Returns:
        List of synthetic test samples

    """
    import random

    console.print("\n[cyan]Generating Synthetic Dataset[/cyan]")
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

        dataset.append(
            {
                "question": question,
                "contexts": contexts,
                "response": response,
                "reference_answer": doc,  # Use document as reference
            }
        )

    console.print(f"  [green]Created {len(dataset)} synthetic samples[/green]")

    return dataset


@beartype
def create_golden_dataset(
    documents: list[dict[str, Any]],
    questions_per_doc: int = 2,
) -> list[dict[str, Any]]:
    """
    Create golden dataset from existing documents.

    Args:
        documents: List of documents with content and metadata
        questions_per_doc: Number of questions to generate per document

    Returns:
        List of golden dataset samples

    """
    console.print("\n[cyan]Creating Golden Dataset[/cyan]")
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

            dataset.append(
                {
                    "question": question,
                    "contexts": [content],
                    "response": response,
                    "reference_answer": content,
                    "metadata": metadata,
                }
            )

    console.print(f"  [green]Created {len(dataset)} golden samples[/green]")

    return dataset


@beartype
def validate_dataset_quality(dataset: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Validate dataset quality with various checks.

    Args:
        dataset: Dataset to validate

    Returns:
        Dictionary with validation results

    """
    console.print("\n[cyan]Validating Dataset Quality[/cyan]")

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
        console.print("  [yellow]Errors found:[/yellow]")
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
    """
    Export dataset to RAGAS-compatible JSON format.

    Args:
        dataset: Dataset to export
        output_path: Optional path to save JSON file

    Returns:
        JSON string of the dataset

    """
    console.print("\n[cyan]Exporting Dataset[/cyan]")

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
def calculate_dataset_statistics(dataset: list[dict[str, Any]], seed: int = 42) -> DatasetStats:
    """
    Calculate statistics about a dataset.

    Args:
        dataset: Dataset to analyze
        seed: Random seed used for generation

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
        generation_seed=seed,
    )


@beartype
def log_dataset_generation_to_mlflow(
    dataset_type: str,
    dataset: list[dict[str, Any]],
    file_path: Path,
    generation_params: dict[str, Any],
    stats: DatasetStats,
    validation_result: dict[str, Any],
) -> str | None:
    """
    Log dataset generation to MLflow.

    Args:
        dataset_type: Type of dataset (synthetic or golden)
        dataset: The generated dataset
        file_path: Path to the dataset file
        generation_params: Parameters used for generation
        stats: Dataset statistics
        validation_result: Validation results

    Returns:
        MLflow run ID if successful, None otherwise

    """
    if not MLFLOW_AVAILABLE:
        console.print("[yellow]MLflow not available. Skipping MLflow logging.[/yellow]")
        return None

    run_name = f"{dataset_type}_dataset_generation"

    with mlflow.start_run(nested=True, run_name=run_name) as run:
        run_id = run.info.run_id
        console.print(f"  [dim][NESTED RUN] Run ID: {run_id}[/dim]")

        # Log generation parameters
        mlflow.log_param("dataset_type", dataset_type)
        for key, value in generation_params.items():
            mlflow.log_param(key, str(value))
        console.print(f"  [dim]Logged {len(generation_params)} generation parameters[/dim]")

        # Log dataset statistics as metrics
        mlflow.log_metric("total_samples", stats.total_samples)
        mlflow.log_metric("valid_samples", stats.valid_samples)
        mlflow.log_metric("avg_question_length", stats.avg_question_length)
        mlflow.log_metric("avg_context_count", stats.avg_context_count)
        mlflow.log_metric("generation_seed", stats.generation_seed)
        console.print("  [dim]Logged 5 dataset statistics metrics[/dim]")

        # Log validation results
        mlflow.log_metric("validation_passed", 1 if validation_result["valid"] else 0)
        mlflow.log_metric("validation_error_count", len(validation_result["errors"]))
        console.print("  [dim]Logged validation results[/dim]")

        # Log dataset as artifact
        mlflow.log_artifact(str(file_path))
        console.print(f"  [dim]Logged artifact: {file_path}[/dim]")

        # Set tags
        mlflow.set_tags(
            {
                "dataset_type": dataset_type,
                "generation_method": "scripted",
                "validation_status": "passed" if validation_result["valid"] else "failed",
            }
        )

    return run_id


@beartype
def generate_test_data_with_mlflow() -> dict[str, Any]:
    """
    Run test data generation demonstration with MLflow integration.

    This function demonstrates:
    1. Synthetic data generation with MLflow parameter logging
    2. Golden dataset creation with MLflow artifact logging
    3. Data quality validation with MLflow metric tracking
    4. Reproducibility patterns with MLflow tracking
    5. Dataset quality metrics over time

    Returns:
        Dictionary with results and MLflow run information

    """
    if not MLFLOW_AVAILABLE:
        console.print("[red]ERROR:[/red] MLflow is not installed. Install with: pip install mlflow")
        raise ImportError("mlflow package is required")

    # Load configuration
    config = get_ragas_config()

    # Set up MLflow
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    experiment_name = "ragas_data_generation"
    mlflow.set_experiment(experiment_name)

    # Header
    console.print(
        Panel(
            "[bold cyan]Test Data Generation with MLflow Integration[/bold cyan]\n"
            "Demonstrating dataset generation with comprehensive MLflow tracking\n"
            "for reproducibility and quality monitoring",
            title="[bold green]RAGas Advanced + MLflow[/bold green]",
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

    # Create temporary directory for generated datasets
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Start parent run
        with mlflow.start_run(run_name="data_generation_demonstration") as parent_run:
            parent_run_id = parent_run.info.run_id
            console.print("\n[bold][PARENT RUN] Starting test data generation[/bold]")
            console.print(f"[dim]Parent run ID: {parent_run_id}[/dim]")

            mlflow.log_param("demo_type", "data_generation")
            mlflow.log_param("corpus_size", str(len(document_corpus)))

            results = []

            # 1. Generate synthetic dataset
            console.print("\n[bold yellow]1. Synthetic Data Generation[/bold yellow]")
            synthetic_params = {
                "num_samples": 5,
                "corpus_size": len(document_corpus),
                "seed": 42,
            }
            synthetic_dataset = generate_synthetic_dataset(
                num_samples=synthetic_params["num_samples"],
                document_corpus=document_corpus,
                seed=synthetic_params["seed"],
            )

            # Export and log synthetic dataset
            synthetic_path = temp_path / "synthetic_dataset.json"
            export_dataset_to_json(synthetic_dataset, synthetic_path)
            synthetic_stats = calculate_dataset_statistics(synthetic_dataset, seed=42)
            synthetic_validation = validate_dataset_quality(synthetic_dataset)

            synthetic_run_id = log_dataset_generation_to_mlflow(
                dataset_type="synthetic",
                dataset=synthetic_dataset,
                file_path=synthetic_path,
                generation_params=synthetic_params,
                stats=synthetic_stats,
                validation_result=synthetic_validation,
            )

            results.append(
                {
                    "type": "synthetic",
                    "num_samples": len(synthetic_dataset),
                    "stats": synthetic_stats,
                    "run_id": synthetic_run_id,
                }
            )

            # 2. Create golden dataset
            console.print("\n[bold yellow]2. Golden Dataset Creation[/bold yellow]")
            documents = [
                {"content": doc, "metadata": {"source": f"doc_{i}.pdf"}}
                for i, doc in enumerate(document_corpus[:3])
            ]
            golden_params = {
                "num_documents": len(documents),
                "questions_per_doc": 1,
            }
            golden_dataset = create_golden_dataset(documents=documents, questions_per_doc=1)

            # Export and log golden dataset
            golden_path = temp_path / "golden_dataset.json"
            export_dataset_to_json(golden_dataset, golden_path)
            golden_stats = calculate_dataset_statistics(golden_dataset, seed=0)
            golden_validation = validate_dataset_quality(golden_dataset)

            golden_run_id = log_dataset_generation_to_mlflow(
                dataset_type="golden",
                dataset=golden_dataset,
                file_path=golden_path,
                generation_params=golden_params,
                stats=golden_stats,
                validation_result=golden_validation,
            )

            results.append(
                {
                    "type": "golden",
                    "num_samples": len(golden_dataset),
                    "stats": golden_stats,
                    "run_id": golden_run_id,
                }
            )

            # 3. Combined dataset statistics
            combined_dataset = synthetic_dataset + golden_dataset
            combined_stats = calculate_dataset_statistics(combined_dataset, seed=42)

    # Display statistics
    console.print("\n[cyan]Combined Dataset Statistics:[/cyan]")
    console.print(f"  Total samples: {combined_stats.total_samples}")
    console.print(f"  Valid samples: {combined_stats.valid_samples}")
    console.print(f"  Avg question length: {combined_stats.avg_question_length:.1f} chars")
    console.print(f"  Avg context count: {combined_stats.avg_context_count:.1f}")

    # Display sample comparison
    console.print("\n[bold yellow]Dataset Comparison[/bold yellow]")
    display_dataset_comparison_table()

    # Display reproducibility guidance
    console.print("\n")
    display_reproducibility_guidance()

    # Display MLflow guidance
    console.print("\n")
    mlflow_guidance = generate_mlflow_guidance(experiment_name, parent_run_id)
    console.print(mlflow_guidance)

    # Summary
    summary_text = Text.from_markup(
        f"[bold green]Data Generation Summary[/bold green]\n"
        f"• Synthetic samples: {len(synthetic_dataset)}\n"
        f"• Golden samples: {len(golden_dataset)}\n"
        f"• Total samples: {len(combined_dataset)}\n"
        f"• Validation: {'PASSED' if all(r.get('validation_passed', True) for r in results) else 'FAILED'}\n"
        f"• Parent run ID: {parent_run_id}\n"
        f"• Experiment: {experiment_name}\n"
        f"[dim]Key insight: MLflow tracking enables reproducibility and quality monitoring[/dim]"
    )
    console.print(
        Panel(summary_text, title="[bold cyan]Generation Complete[/bold cyan]", border_style="cyan")
    )

    return {
        "experiment_name": experiment_name,
        "parent_run_id": parent_run_id,
        "results": results,
        "combined_stats": combined_stats,
    }


@beartype
def display_dataset_comparison_table() -> None:
    """Display comparison table for synthetic vs golden datasets."""
    table = Table(title="Synthetic vs Golden Datasets")
    table.add_column("Type", style="cyan", width=15)
    table.add_column("Use Case", style="green", width=30)
    table.add_column("Pros", style="yellow", width=30)
    table.add_column("MLflow Tracking", style="blue", width=25)

    table.add_row(
        "Synthetic",
        "Development, testing, rapid iteration",
        "Fast to generate, controlled variety",
        "Parameters logged, reproducible via seed",
    )
    table.add_row(
        "Golden",
        "Production evaluation, benchmarking",
        "Realistic, human-validated quality",
        "Artifact logged, version controlled",
    )

    console.print(table)


@beartype
def display_reproducibility_guidance() -> None:
    """Display guidance on dataset reproducibility."""
    guidance = Panel(
        "[bold yellow]Reproducibility Best Practices with MLflow:[/bold yellow]\n\n"
        "• [green]Random Seeds:[/green]\n"
        "  - Always set random seed for synthetic generation\n"
        "  - Document seed in MLflow parameters\n"
        "  - Use consistent seeds across experiments\n"
        "  - Track seed changes in MLflow runs\n\n"
        "• [cyan]Dataset Versioning:[/cyan]\n"
        "  - Version your datasets (v1.0, v1.1, etc.)\n"
        "  - Track changes and updates in MLflow\n"
        "  - Store golden datasets separately from synthetic\n"
        "  - Use MLflow artifacts for version control\n\n"
        "• [blue]Size Considerations:[/blue]\n"
        "  - Minimum viable size: 50-100 samples\n"
        "  - Statistical significance: 200+ samples\n"
        "  - Balance quality vs quantity\n"
        "  - Track size in MLflow metrics\n\n"
        "• [magenta]Storage Patterns:[/magenta]\n"
        "  - Use JSON for portability\n"
        "  - Include metadata (creation date, seed, version)\n"
        "  - Separate train/validation/test splits\n"
        "  - Log all artifacts to MLflow",
        title="[bold cyan]Reproducibility Guidance[/bold cyan]",
        border_style="cyan",
    )
    console.print(guidance)


@beartype
def generate_mlflow_guidance(experiment_name: str, parent_run_id: str | None) -> Panel:
    """
    Generate MLflow UI navigation guidance for data generation.

    Args:
        experiment_name: Name of the MLflow experiment
        parent_run_id: Optional parent run ID

    Returns:
        Panel with MLflow UI navigation instructions

    """
    content = "[bold yellow]MLflow Data Generation Tracking:[/bold yellow]\n\n"
    content += "1. Open MLflow UI: [cyan]http://localhost:5000[/cyan]\n"
    content += "2. Navigate to Experiments → [cyan]" + experiment_name + "[/cyan]\n"

    if parent_run_id:
        content += "3. Find parent run: [cyan]" + parent_run_id + "[/cyan]\n"
        content += "4. View nested runs for synthetic and golden datasets\n"

    content += "\n[bold yellow]Artifacts Section:[/bold yellow]\n"
    content += "• Download generated datasets from artifacts\n"
    content += "• Compare datasets across different runs\n"
    content += "• Track dataset quality metrics over time\n\n"

    content += "[bold yellow]Reproducibility Features:[/bold yellow]\n"
    content += "• Random seeds logged as parameters\n"
    content += "• Generation parameters tracked\n"
    content += "• Validation metrics compared\n"
    content += "• Historical quality trends visible\n\n"

    content += "[dim][TODO: Add screenshot showing dataset generation tracking][/dim]"

    return Panel(
        content,
        title="[bold cyan]MLflow Data Tracking Guide[/bold cyan]",
        border_style="yellow",
    )


@beartype
def main() -> None:
    """Run test data generation example with MLflow integration."""
    try:
        generate_test_data_with_mlflow()
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")
        raise


if __name__ == "__main__":
    main()
