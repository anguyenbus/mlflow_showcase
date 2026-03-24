"""Nested span tracing example for MLflow UI screenshot.

This example demonstrates parent-child span relationships
where one function calls another, creating a nested span hierarchy.

Expected Output:
--------------
Running nested functions...
parent_function calling child_function
child_function(5, 3) = 8
parent_function result: 8

Trace ID: trace-id-here
View in MLflow UI to see the span hierarchy!
"""

import mlflow

def main():
    """Run nested span tracing example."""
    # Setup MLflow
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("mlflow-tracing-decorators")

    print("Running nested functions...")

    # Example: Nested function calls with tracing
    @mlflow.trace
    def child_function(a: int, b: int) -> int:
        """Child function that adds two numbers."""
        print(f"child_function({a}, {b}) = {a + b}")
        return a + b

    @mlflow.trace
    def parent_function(x: int, y: int) -> int:
        """Parent function that calls child function."""
        print("parent_function calling child_function")
        result = child_function(x, y)
        print(f"parent_function result: {result}")
        return result

    # Run the nested functions
    with mlflow.start_run():
        result = parent_function(5, 3)

    print(f"\nTrace completed!")
    print("View in MLflow UI to see the nested span hierarchy:")
    print("  parent_function (parent span)")
    print("  └── child_function (child span)")

if __name__ == "__main__":
    main()
