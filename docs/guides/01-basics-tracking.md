# Basics: MLflow Tracking and Logging

This guide walks through the fundamentals of MLflow tracking and logging for LLM applications. You'll learn how to track experiments, log parameters and metrics, and save artifacts.

## Prerequisites

Before starting this guide, ensure you have:

1. Python 3.10+ installed
2. Zhipu AI API key ([Get one here](https://open.bigmodel.cn/))
3. Completed the project setup from the main README

## Setup

1. **Set up your environment:**

```bash
# Install dependencies
uv sync --all-extras --dev

# Activate your virtual environment
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

2. **Configure environment variables:**

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Zhipu AI API key
# ZHIPU_API_KEY=your_api_key_here
```

3. **Start the MLflow tracking server:**

```bash
# In a separate terminal, start MLflow UI
mlflow ui --backend-store-uri sqlite:///mlflow.db

# The UI will be available at http://localhost:5000
```

## Exercise 1: Basic Experiment Tracking

Learn how to create experiments and log parameters/metrics.

1. **Run the basic tracking example:**

```bash
uv run python src/basics/mlflow_tracking.py
```

2. **Expected output:**

```
INFO: 'basics_tracking' experiment does not exist. Creating a new one
Starting MLflow run with name basic_tracking_run
Logged parameter: learning_rate = 0.001
Logged parameter: model_name = glm-5-flash
Logged metric: accuracy = 0.85
Logged metric: loss = 0.15
Logged metric: accuracy = 0.87
Logged metric: loss = 0.12
Logged artifact: model_predictions.csv
Run finished. View at: http://localhost:5000/experiments/...
```

3. **Verify in MLflow UI:**

- Open http://localhost:5000 in your browser
- Click on the "basics_tracking" experiment
- You should see:
  - Parameters: `learning_rate`, `model_name`
  - Metrics: `accuracy` (0.85, 0.87), `loss` (0.15, 0.12)
  - Artifacts: `model_predictions.csv`

## Exercise 2: Model Logging

Learn how to log LangChain models with MLflow.

1. **Run the model logging example:**

```bash
uv run python src/basics/model_logging.py
```

2. **Expected output:**

```
Creating LangChain chain...
Logging model to MLflow...
Model logged successfully
Model URI: mlflow-artifacts:/...
Loading model back from MLflow...
Invoking loaded model...
Response: This is a test response from the model
```

3. **Verify in MLflow UI:**

- Navigate to the experiment run
- Click on the "Artifacts" section
- You should see:
  - `model/` directory with MLflow model files
  - `MLmodel` metadata file
  - Model signature and input examples

## Exercise 3: Metric Helpers

Learn how to use custom metric logging helpers.

1. **Run the metrics helpers example:**

```bash
uv run python src/basics/metrics_helpers.py
```

2. **Expected output:**

```
Logging custom metrics...
Logged metric: precision = 0.92
Logged metric: recall = 0.88
Logged metric: f1_score = 0.90
Logging batch metrics...
Logged 3 metrics in batch
```

3. **Key concepts:**

- **Custom metrics**: Define domain-specific metrics for your use case
- **Batch logging**: Log multiple metrics efficiently
- **Metric history**: Track metrics over time during training

## Understanding MLflow Concepts

### Experiments

Experiments are the primary organizational unit in MLflow. Each experiment contains multiple runs.

```python
import mlflow

# Create or set an experiment
mlflow.set_experiment("my_experiment")
```

### Runs

A run represents a single execution of your model or training script.

```python
# Start a run
with mlflow.start_run():
    # Your code here
    mlflow.log_param("param_name", param_value)
    mlflow.log_metric("metric_name", metric_value)
```

### Parameters

Parameters are inputs to your model that don't change during a run.

```python
mlflow.log_param("learning_rate", 0.001)
mlflow.log_param("batch_size", 32)
```

### Metrics

Metrics are numerical values that can change during a run (e.g., accuracy, loss).

```python
# Log a single metric
mlflow.log_metric("accuracy", 0.85)

# Log multiple values over time
for epoch in range(10):
    accuracy = train_one_epoch()
    mlflow.log_metric("accuracy", accuracy, step=epoch)
```

### Artifacts

Artifacts are output files from your runs (models, plots, datasets).

```python
# Log a file
mlflow.log_artifact("predictions.csv")

# Log a directory
mlflow.log_artifacts("model_files/")
```

## Verification Checklist

Before moving to the next guide, verify:

- [ ] MLflow UI is accessible at http://localhost:5000
- [ ] You can see the "basics_tracking" experiment
- [ ] Parameters and metrics appear correctly in the UI
- [ ] Artifacts are logged and downloadable
- [ ] Model logging and loading works end-to-end
- [ ] You understand the difference between parameters and metrics

## Troubleshooting

**Issue: MLflow UI doesn't show experiments**

- Solution: Ensure you started the MLflow UI with the correct backend store URI:
  ```bash
  mlflow ui --backend-store-uri sqlite:///mlflow.db
  ```

**Issue: API key errors**

- Solution: Verify your `.env` file contains a valid `ZHIPU_API_KEY`

**Issue: Artifacts not logging**

- Solution: Check file paths are correct relative to where you run the script

## Next Steps

Once you've completed this guide, move on to:

- **[02-tracing-deep-dive.md](02-tracing-deep-dive.md)** - Learn about MLflow tracing for LLM observability
- **[03-evaluation-framework.md](03-evaluation-framework.md)** - Understand evaluation metrics and frameworks
- **[04-rag-implementation.md](04-rag-implementation.md)** - Build advanced RAG systems

## Additional Resources

- [MLflow Tracking Documentation](https://mlflow.org/docs/latest/tracking.html)
- [MLflow Python API](https://mlflow.org/docs/latest/python_api/index.html)
- Project source code: @src/basics/
