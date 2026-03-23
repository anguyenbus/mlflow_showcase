"""Decorator-based tracing example with MLflow.

This example demonstrates how to use @mlflow.trace decorator
for automatic function instrumentation.

Expected Output:
--------------
add_numbers(5, 3) = 8
Trace ID: trace-id-here
Now run `mlflow server` and open MLflow UI to see the trace visualization!
"""


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from rich.console import Console

import mlflow
from config import get_config
from basics.mlflow_utils import create_experiment


# Initialize console
console = Console()


def main() -> None:
    """Run decorator-based tracing example."""
    # Setup MLflow
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    experiment = create_experiment("mlflow-tracing-decorators")

    # Enable automatic tracing
    # NOTE: No need to explicitly enable, @mlflow.trace works out of the box

    # Example 1: Simple decorator tracing
    @mlflow.trace
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    # Example 2: Decorator with metadata
    @mlflow.trace(
        span_type="math",
        attributes={"operation": "multiplication"},
    )
    def multiply_numbers(a: int, b: int) -> int:
        """Multiply two numbers together."""
        return a * b

    # Start MLflow run to capture traces
    with mlflow.start_run():
        console.print("[cyan]Running traced functions...[/cyan]\n")

        # Call traced functions
        result1 = add_numbers(5, 3)
        console.print(f"add_numbers(5, 3) = {result1}\n")

        result2 = multiply_numbers(4, 7)
        console.print(f"multiply_numbers(4, 7) = {result2}\n")

        # Get the last trace ID
        trace_id = mlflow.get_last_active_trace_id()
        console.print(f"[cyan]Trace ID:[/cyan] {trace_id}")

        # Retrieve and display trace
        trace = mlflow.get_trace(trace_id)
        console.print("\n[green]Trace data:[/green]")
        console.print(trace.to_json(pretty=True))

        console.print(
            "\n[green]Now run `mlflow ui` and open MLflow UI to see traces![/green]"
        )


def process_with_manual_span(input_data: str) -> str:
    """Process data with manual span creation.

    Args:
        input_data: Input string to process

    Returns:
        Processed string
    """
    with mlflow.start_span(name="process_data") as span:
        span.set_inputs({"input": input_data})
        result = f"processed: {input_data}"
        span.set_outputs({"output": result})
        return result


def nested_function_call(x: int) -> int:
    """Demonstrate nested spans with parent-child relationships.

    Args:
        x: Input value

    Returns:
        Squared value
    """
    with mlflow.start_span(name="outer_function") as outer_span:
        outer_span.set_inputs({"x": x})

        # Nested span
        with mlflow.start_span(name="inner_function") as inner_span:
            inner_span.set_inputs({"x": x})
            result = x * x
            inner_span.set_outputs({"result": result})

        outer_span.set_outputs({"result": result})
        return result


if __name__ == "__main__":
    main()
