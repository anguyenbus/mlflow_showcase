"""Trace search and inspection example.

This example demonstrates how to search traces using
mlflow.search_traces() and inspect trace data.

Expected Output:
--------------
Running traced functions...
Searching for traces...
Found 5 traces
Trace 1: ID=xxx, Timestamp=xxx, Span Count=3
Trace 2: ID=yyy, Timestamp=yyy, Span Count=2
Filtering traces by experiment...
Found 3 traces in experiment 'mlflow-trace-search'
"""


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from rich.console import Console
import time

import mlflow
from config import get_config


# Initialize console
console = Console()


@mlflow.trace
def process_item(item_id: int) -> str:
    """Process an item with tracing."""
    time.sleep(0.1)
    return f"processed_{item_id}"


@mlflow.trace
def batch_process(item_ids: list[int]) -> list[str]:
    """Process multiple items."""
    results = []
    for item_id in item_ids:
        result = process_item(item_id)
        results.append(result)
    return results


def main() -> None:
    """Run trace search example."""
    # Setup MLflow
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    experiment = mlflow.set_experiment("mlflow-trace-search")

    console.print("Running traced functions...\n")

    # Start run and generate traces
    with mlflow.start_run():
        # Generate some traces
        batch_process([1, 2, 3])
        batch_process([4, 5])

        console.print("Searching for traces...\n")

        # Search all traces
        traces = mlflow.search_traces(
            filter_string="timestamp > 0",
            max_results=10,
        )

        console.print(f"[green]Found {len(traces)} traces[/green]\n")

        # Display trace information
        for i, trace_id in enumerate(traces[:5], 1):
            trace = mlflow.get_trace(trace_id)
            if trace is None:
                continue
            console.print(f"[cyan]Trace {i}:[/cyan]")
            console.print(f"  ID: {trace.info.trace_id}")
            console.print(f"  Timestamp: {trace.info.timestamp_ms}")
            console.print(f"  Span Count: {len(trace.data.spans)}")
            console.print(f"  Experiment ID: {trace.info.experiment_id}\n")

        # Search traces by experiment
        console.print(f"Filtering traces by experiment: {experiment.experiment_id}\n")

        experiment_traces = mlflow.search_traces(
            locations=[experiment.experiment_id],
            max_results=10,
        )

        console.print(f"[green]Found {len(experiment_traces)} traces[/green] in experiment\n")

        # Search traces by run ID
        mlflow.end_run()  # End previous run
        with mlflow.start_run() as run:
            batch_process([6, 7, 8])

            run_traces = mlflow.search_traces(
                filter_string=f"run_id = '{run.info.run_id}'",
                max_results=10,
            )

            console.print(f"[green]Found {len(run_traces)} traces[/green] in run {run.info.run_id}\n")

            # Display first trace from run
            if len(run_traces) > 0:
                # run_traces is a DataFrame, get first trace ID
                trace_id = run_traces.iloc[0, 0] if len(run_traces.columns) > 0 else None
                if trace_id:
                    trace = mlflow.get_trace(trace_id)
                    if trace:
                        console.print(f"[cyan]Sample trace:[/cyan]")
                        console.print(f"  ID: {trace.info.trace_id}")
                        console.print(f"  Span Count: {len(trace.data.spans)}\n")

        console.print("[green]View in MLflow UI to explore all traces![/green]")


if __name__ == "__main__":
    main()
