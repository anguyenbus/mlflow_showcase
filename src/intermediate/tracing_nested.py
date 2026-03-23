"""Nested spans example demonstrating call hierarchy.

This example shows parent-child span relationships and
timing information in MLflow traces.

Expected Output:
--------------
Fetching data from API...
Processing data: 1000 records
Generating report: Report contains 3 sections
Pipeline completed successfully
Total execution time: X.XX seconds
"""


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
import time
from rich.console import Console

import mlflow
from config import get_config


# Initialize console
console = Console()


def fetch_data(api_url: str) -> list[dict]:
    """Fetch data from API endpoint."""
    with mlflow.start_span(name="fetch_data", attributes={"api_url": api_url}) as span:
        span.set_inputs({"url": api_url})

        console.print("Fetching data from API...")

        # Simulate API call
        time.sleep(0.5)
        data = [{"id": i, "value": f"item_{i}"} for i in range(1000)]

        span.set_outputs({"record_count": len(data)})
        return data


def process_data(data: list[dict]) -> list[dict]:
    """Process and transform data."""
    with mlflow.start_span(name="process_data") as span:
        span.set_inputs({"input_count": len(data)})

        console.print(f"Processing data: {len(data)} records")

        # Simulate data processing
        time.sleep(0.3)
        processed = [{"id": d["id"], "value_upper": d["value"].upper()} for d in data]

        span.set_outputs({"output_count": len(processed)})
        return processed


def generate_report(data: list[dict]) -> str:
    """Generate analysis report."""
    with mlflow.start_span(name="generate_report") as span:
        span.set_inputs({"data_count": len(data)})

        console.print("Generating report...")

        # Simulate report generation
        time.sleep(0.2)
        report = f"Report contains {len(data)} sections"

        span.set_outputs({"report_length": len(report)})
        return report


def run_data_pipeline(api_url: str) -> dict[str, any]:
    """Run complete data pipeline with nested spans.

    Args:
        api_url: API endpoint URL

    Returns:
        Pipeline execution results
    """
    with mlflow.start_span(name="run_data_pipeline") as root_span:
        root_span.set_inputs({"api_url": api_url})

        # Nested calls create child spans
        data = fetch_data(api_url)
        processed = process_data(data)
        report = generate_report(processed)

        result = {
            "data_count": len(data),
            "processed_count": len(processed),
            "report": report,
        }

        root_span.set_outputs(result)
        console.print("Pipeline completed successfully")
        return result


def main() -> None:
    """Run nested spans example."""
    # Setup MLflow
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    mlflow.set_experiment("mlflow-nested-spans")

    # Start run and execute pipeline
    with mlflow.start_run() as run:
        start_time = time.time()

        result = run_data_pipeline("https://api.example.com/data")

        execution_time = time.time() - start_time

        console.print(f"\n[cyan]Total execution time:[/cyan] {execution_time:.2f}s")
        console.print(f"\n[cyan]Run ID:[/cyan] {run.info.run_id}")
        console.print("\n[green]View in MLflow UI to see nested span hierarchy![/green]")


if __name__ == "__main__":
    main()
