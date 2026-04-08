#!/usr/bin/env python
"""
Simple RAGAS evaluation with MLflow manual logging.

This script demonstrates:
1. Running RAGAS evaluation with Zhipu AI backend
2. Manually logging results to MLflow
3. Logging parameters, metrics, and artifacts
"""

import os
import pandas as pd
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()


def main():
    """Run RAGAS evaluation with MLflow manual logging."""
    try:
        # Step 1: Load configuration
        console.print("[bold cyan]Step 1:[/bold cyan] Loading configuration...")
        from ragas_evaluation.shared.config import get_ragas_config
        config = get_ragas_config()
        console.print(f"[green]✓[/green] MLflow tracking URI: {config.mlflow_tracking_uri}")

        # Step 2: Set up environment for RAGAS to use Zhipu AI
        os.environ["OPENAI_API_KEY"] = config.zhipu_api_key
        os.environ["OPENAI_BASE_URL"] = "https://open.bigmodel.cn/api/paas/v4/"

        # Step 3: Load evaluation dataset
        console.print("\n[bold cyan]Step 2:[/bold cyan] Loading evaluation dataset...")
        from ragas_evaluation.shared.data_loader import get_evaluation_dataset_path
        import json

        data_path = get_evaluation_dataset_path()
        with open(data_path) as f:
            dataset = json.load(f)
        console.print(f"[green]✓[/green] Loaded {len(dataset)} evaluation examples")

        # Step 4: Prepare data for RAGAS
        console.print("\n[bold cyan]Step 3:[/bold cyan] Preparing data for RAGAS...")

        df = pd.DataFrame(dataset)
        df_renamed = df.rename(columns={
            "question": "user_input",
            "contexts": "retrieved_contexts",
            "response": "response",
            "reference_answer": "reference"
        })

        from datasets import Dataset as HFDataset
        hf_dataset = HFDataset.from_pandas(df_renamed)
        console.print("[green]✓[/green] Data prepared for RAGAS evaluation")

        # Step 5: Create RAGAS metrics
        console.print("\n[bold cyan]Step 4:[/bold cyan] Creating RAGAS metrics...")

        from ragas.metrics._faithfulness import faithfulness
        from ragas.metrics._context_precision import context_precision
        from ragas.llms.base import llm_factory
        from openai import OpenAI as OpenAIClient
        from ragas.run_config import RunConfig

        # Create Zhipu AI client
        client = OpenAIClient(
            api_key=config.zhipu_api_key,
            base_url="https://open.bigmodel.cn/api/paas/v4/"
        )

        # Create LLM
        ragas_llm = llm_factory(model="glm-5", client=client, max_tokens=4096)

        # Inject LLM into metrics
        faithfulness.llm = ragas_llm
        context_precision.llm = ragas_llm

        run_config = RunConfig(max_retries=3, max_wait=60, timeout=60)
        metrics = [faithfulness, context_precision]
        console.print("[green]✓[/green] Created RAGAS evaluation with metrics:")
        for metric in metrics:
            console.print(f"  - {metric.name}")

        # Step 6: Run evaluation
        console.print("\n[bold cyan]Step 5:[/bold cyan] Running RAGAS evaluation...")

        from ragas import evaluate

        results = evaluate(
            dataset=hf_dataset,
            metrics=metrics,
            run_config=run_config,
        )
        console.print("[green]✓[/green] Evaluation complete!")

        # Step 7: Extract results
        results_df = results.to_pandas()
        metric_results = {}
        for metric in ["faithfulness", "context_precision"]:
            if metric in results_df.columns:
                scores = results_df[metric].dropna()
                if len(scores) > 0:
                    metric_results[metric] = scores.mean()

        # Display results
        console.print("\n[bold green]Evaluation Results:[/bold green]")
        for name, score in metric_results.items():
            console.print(f"  {name}: {score:.4f}")

        # Step 8: Log to MLflow
        console.print("\n[bold cyan]Step 6:[/bold cyan] Logging to MLflow...")

        import mlflow

        experiment_name = "ragas-simple-manual-logging"
        mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        mlflow.set_experiment(experiment_name)

        with mlflow.start_run() as run:
            run_id = run.info.run_id

            # Log parameters
            mlflow.log_param("model", "glm-5")
            mlflow.log_param("backend", "zhipu")
            mlflow.log_param("num_samples", str(len(dataset)))
            mlflow.log_param("max_tokens", "4096")
            mlflow.log_params({f"metric_{i}": m for i, m in enumerate(["faithfulness", "context_precision"])})

            # Log metrics
            for name, score in metric_results.items():
                mlflow.log_metric(name, score)
            mlflow.log_metric("average_score", sum(metric_results.values()) / len(metric_results))

            # Log dataset as artifact
            mlflow.log_artifact(data_path, "evaluation_dataset.json")

            # Set tags
            mlflow.set_tags({
                "evaluation_type": "ragas",
                "backend": "zhipu",
                "domain": "tax_evaluation",
                "logging_method": "manual",
            })

            console.print(f"[green]✓[/green] Logged to MLflow")
            console.print(f"  Run ID: {run_id}")
            console.print(f"  Experiment: {experiment_name}")

        # Display run information
        console.print("\n")
        console.print(Panel.fit(
            f"""MLflow Run Information
• Run ID: {run_id[:8]}...
• Experiment: ragas-simple-manual-logging
• View at: {config.mlflow_tracking_uri}/#/experiments/...
""",
            title="MLflow Logging Complete",
            border_style="cyan",
        ))

        console.print("\n")
        console.print(Panel(
            "[yellow]SCREENSHOT CHECKPOINT[/yellow]\n"
            "\n1. Open MLflow UI at http://localhost:5000\n"
            "2. Click on experiment: ragas-simple-manual-logging\n"
            "3. Click on the latest run\n"
            "4. Take screenshot showing:\n"
            "   - Parameters section\n"
            "   - Metrics section\n"
            "   - Artifacts section\n"
            "\n5. Suggested filename: mlflow_manual_logging.png",
            title="Screenshot",
            border_style="yellow",
        ))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {e}")
        raise


if __name__ == "__main__":
    main()
