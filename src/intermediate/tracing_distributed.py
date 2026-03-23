"""Distributed tracing example across multiple functions.

This example demonstrates trace correlation across multiple
function calls and trace retrieval with mlflow.get_trace().

Expected Output:
--------------
Querying database for user: user_123
Fetching user profile from external service
Calculating user recommendations
Updating user statistics
User workflow completed
Trace ID: trace-id-here
Found 2 traces for this workflow
"""


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from rich.console import Console

import mlflow
from config import get_config


# Initialize console
console = Console()


def query_user_database(user_id: str) -> dict[str, any]:
    """Query user information from database."""
    with mlflow.start_span(name="query_database") as span:
        span.set_inputs({"user_id": user_id})
        console.print(f"Querying database for user: {user_id}")

        # Simulate database query
        user_data = {
            "user_id": user_id,
            "name": "John Doe",
            "email": "john@example.com",
        }

        span.set_outputs({"found": True})
        return user_data


def fetch_external_profile(user_id: str) -> dict[str, any]:
    """Fetch user profile from external service."""
    with mlflow.start_span(name="fetch_external_profile") as span:
        span.set_inputs({"user_id": user_id})
        console.print("Fetching user profile from external service")

        # Simulate API call
        profile = {
            "user_id": user_id,
            "interests": ["python", "mlflow", "llms"],
            "score": 85,
        }

        span.set_outputs({"profile_complete": True})
        return profile


def calculate_recommendations(profile: dict[str, any]) -> list[str]:
    """Calculate personalized recommendations."""
    with mlflow.start_span(name="calculate_recommendations") as span:
        span.set_inputs({"interests": profile.get("interests", [])})
        console.print("Calculating user recommendations")

        # Simulate recommendation logic
        recommendations = [
            "Advanced Python Course",
            "MLflow Tutorial",
            "LLM Observability Guide",
        ]

        span.set_outputs({"recommendation_count": len(recommendations)})
        return recommendations


def update_user_stats(user_id: str, action: str) -> None:
    """Update user statistics."""
    with mlflow.start_span(name="update_statistics") as span:
        span.set_inputs({"user_id": user_id, "action": action})
        console.print("Updating user statistics")
        span.set_outputs({"updated": True})


def run_user_workflow(user_id: str) -> dict[str, any]:
    """Run distributed user workflow across multiple functions.

    Args:
        user_id: User identifier

    Returns:
        Workflow results
    """
    with mlflow.start_span(name="user_workflow") as root_span:
        root_span.set_inputs({"user_id": user_id})

        # Distributed function calls
        user_data = query_user_database(user_id)
        profile = fetch_external_profile(user_id)
        recommendations = calculate_recommendations(profile)
        update_user_stats(user_id, "workflow_completed")

        result = {
            "user": user_data,
            "recommendations": recommendations,
            "profile_score": profile.get("score", 0),
        }

        root_span.set_outputs(result)
        console.print("User workflow completed")
        return result


def main() -> None:
    """Run distributed tracing example."""
    # Setup MLflow
    config = get_config()
    mlflow.set_tracking_uri(config.mlflow_tracking_uri)
    mlflow.set_experiment("mlflow-distributed-tracing")

    # Start run and execute workflow
    with mlflow.start_run():
        result = run_user_workflow("user_123")

        # Get trace information
        trace_id = mlflow.get_last_active_trace_id()
        console.print(f"\n[cyan]Trace ID:[/cyan] {trace_id}")

        # Retrieve the trace
        trace = mlflow.get_trace(trace_id)
        console.print(f"\n[green]Trace spans:[/green] {len(trace.data.spans)}")

        # Search for traces
        traces = mlflow.search_traces(
            filter_string="timestamp > 0",
            max_results=10,
        )
        console.print(f"\n[cyan]Found {len(traces)} traces[/cyan] for this workflow")

        console.print("\n[green]View in MLflow UI to see trace correlation![/green]")


if __name__ == "__main__":
    main()
