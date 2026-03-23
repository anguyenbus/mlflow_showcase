"""Manual span tracing example with MLflow.

This example demonstrates fine-grained control over tracing
using mlflow.start_span() context manager.

Expected Output:
--------------
Processing document: test.txt
✓ Extracted text: 100 characters
✓ Analyzed sentiment: positive
Document processing completed
Trace ID: trace-id-here
"""


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from rich.console import Console

import mlflow
from config import get_config


# Initialize console
console = Console()


def extract_text(file_path: str) -> str:
    """Extract text from a document file."""
    with mlflow.start_span(name="extract_text") as span:
        span.set_inputs({"file_path": file_path})
        # Simulate text extraction
        text = "Sample document text for analysis. " * 5
        span.set_outputs({"text_length": len(text)})
        return text


def analyze_sentiment(text: str) -> str:
    """Analyze sentiment of text."""
    with mlflow.start_span(name="analyze_sentiment") as span:
        span.set_inputs({"text_length": len(text)})
        # Simulate sentiment analysis
        sentiment = "positive"
        span.set_outputs({"sentiment": sentiment})
        return sentiment


def process_document(file_path: str) -> dict[str, str]:
    """Process document with fine-grained span control.

    Args:
        file_path: Path to document file

    Returns:
        Dictionary with processing results
    """
    with mlflow.start_span(name="process_document") as span:
        span.set_inputs({"file_path": file_path})

        console.print(f"Processing document: {file_path}")

        # Extract text
        text = extract_text(file_path)
        console.print(f"✓ Extracted text: {len(text)} characters")

        # Analyze sentiment
        sentiment = analyze_sentiment(text)
        console.print(f"✓ Analyzed sentiment: {sentiment}")

        result = {
            "file_path": file_path,
            "text_length": len(text),
            "sentiment": sentiment,
        }

        span.set_outputs(result)
        console.print("Document processing completed")
        return result


def main() -> None:
    """Run manual span tracing example."""
    # Setup MLflow
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    mlflow.set_experiment("mlflow-manual-spans")

    # Start run and trace document processing
    with mlflow.start_run():
        result = process_document("test.txt")

        # Get trace info
        trace_id = mlflow.get_last_active_trace_id()
        console.print(f"\n[cyan]Trace ID:[/cyan] {trace_id}")
        console.print("\n[green]View in MLflow UI to see span hierarchy![/green]")


if __name__ == "__main__":
    main()
