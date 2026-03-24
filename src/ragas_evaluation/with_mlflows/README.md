# RAGas Evaluation with MLflow Integration

This directory demonstrates comprehensive MLflow integration for tracking RAGas evaluation experiments over time, enabling systematic comparison and optimization of RAG systems.

## Overview

MLflow integration provides two approaches for tracking RAGas evaluations:

1. **Automatic Logging** (`auto_logging.py`): One-line evaluation with automatic parameter and metric tracking
2. **Manual Logging** (`manual_logging.py`): Fine-grained control over what gets logged

Both approaches enable:
- Experiment tracking and comparison
- Parameter and metric visualization
- Artifact storage (datasets, models)
- Custom tagging for organization

## Prerequisites

Before running these examples, ensure you have:

1. **Set up your API key** in `.env` file:
   ```bash
   ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

2. **Start MLflow UI** (required for viewing results):
   ```bash
   uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
   ```

   Then open: http://localhost:5000

3. **Install dependencies** (if needed):
   ```bash
   uv sync --all-extras --dev
   ```

---

## Comparison: Automatic vs Manual Logging

| Aspect | Automatic Logging | Manual Logging |
|--------|------------------|----------------|
| **Simplicity** | One-line evaluation | Multiple logging calls |
| **Control** | Standardized format | Full customization |
| **Parameters** | Automatic capture | Custom selection |
| **Metrics** | All metrics logged | Selective logging |
| **Tags** | Default tags | Custom tags |
| **Use Case** | Quick evaluation | Custom experiments |
| **Code** | Less code | More code |
| **Flexibility** | Limited | High |

**When to use Automatic Logging:**
- Quick evaluation runs
- Standard metrics tracking
- Learning MLflow integration
- Consistent format across runs

**When to use Manual Logging:**
- Custom parameters needed
- Selective metric logging
- Complex experiments
- Production workflows

---

## Examples

### 1. Automatic Logging (`auto_logging.py`)

**Overview:** Demonstrates MLflow's automatic evaluation logging with ragas integration.

**What it demonstrates:**
- Automatic parameter capture
- Automatic metric logging
- Artifact storage
- UI URL generation
- Screenshot checkpoints

**Run the example:**
```bash
uv run python src/ragas_evaluation/with_mlflows/auto_logging.py
```

**Expected output:**
```
Step 1: Loading configuration...
✓ MLflow tracking URI: sqlite:///mlflow.db

Step 2: Loading evaluation dataset...
Loading evaluation dataset from: /path/to/evaluation_dataset.json
✓ Loaded 6 evaluation examples

Step 3: Configuring Zhipu AI backend...
✓ Configured Zhipu AI backend for RAGas evaluation: glm-5
  Temperature: 0.2 (low for consistent evaluation)
  Embeddings: embedding-3

Step 4: Creating RAGas evaluation...
✓ Created RAGas evaluation with metrics:
  - faithfulness
  - answer_relevancy
  - context_precision
  - context_recall
  - answer_correctness

Step 5: Converting dataset to DataFrame...
✓ Converted dataset to DataFrame: 6 rows

Step 6: Setting up MLflow experiment...
✓ Using MLflow experiment: ragas-auto-logging

Step 7: Running MLflow evaluation with automatic logging...
✓ MLflow evaluation complete!

MLflow Run Information:
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field                 ┃ Value                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ Run ID                │ abc123def456          │
│ Experiment            │ ragas-auto-logging    │
│ Status                │ COMPLETED             │
└───────────────────────┴──────────────────────┘

View results in MLflow UI: http://localhost:5000/#/runs/abc123def456

╭─────────────────────────────────────────────────────────────────╮
│ SCREENSHOT CHECKPOINT                                          │
├─────────────────────────────────────────────────────────────────┤
│ 1. Open MLflow UI at http://localhost:5000                      │
│ 2. Navigate to Experiments → ragas-auto-logging                 │
│ 3. Click on the latest run                                      │
│ 4. Take screenshot of metrics view                              │
│ 5. Suggested filename: mlflow_auto_logging_metrics.png          │
│                                                                 │
│ Capture: Metrics table showing all ragas scores                 │
╰─────────────────────────────────────────────────────────────────╯

Automatic Logging Summary
• Dataset size: 6 examples
• Metrics logged automatically: 5
• Run ID: abc123def456
• Experiment: ragas-auto-logging
• Tracking URI: sqlite:///mlflow.db
```

**Key MLflow APIs:**
```python
import mlflow
import pandas as pd

# Set experiment
mlflow.set_experiment("ragas-auto-logging")

# Automatic evaluation with logging
result = mlflow.evaluate(
    data=df,
    targets="response",
    evaluators=["ragas"],
    evaluator_config={
        "ragas": {
            "metrics": eval_config["metrics"],
            "column_mapping": {
                "question": "question",
                "contexts": "contexts",
                "response": "response",
                "ground_truth": "reference_answer",
            },
        }
    },
)
```

**Screenshot checkpoints:**
1. **MLflow Experiments View**: Show all runs in `ragas-auto-logging` experiment
   - Navigate to: Experiments → ragas-auto-logging
   - Filename: `mlflow_auto_experiments_list.png`

2. **Run Metrics View**: Show detailed metrics for a single run
   - Click on latest run
   - Filename: `mlflow_auto_logging_metrics.png`

3. **Parameters View**: Show automatically logged parameters
   - Click on "Parameters" tab
   - Filename: `mlflow_auto_logging_params.png`

**Real-World Use Cases:**
- **Experiment tracking**: Track multiple evaluation runs over time
- **Model comparison**: Compare different retrieval strategies
- **Regression testing**: Ensure system changes don't degrade quality
- **Performance monitoring**: Track metrics trends across deployments

**Key concepts learned:**
- **Automatic logging**: MLflow's built-in evaluation tracking
- **Experiment organization**: Grouping related runs
- **Parameter capture**: Automatic tracking of configuration
- **Metric visualization**: Built-in charts and comparisons

---

### 2. Manual Logging (`manual_logging.py`)

**Overview:** Demonstrates fine-grained control over MLflow logging for custom evaluation workflows.

**What it demonstrates:**
- Manual parameter logging
- Manual metric logging
- Artifact storage
- Custom tags
- Comparison with auto-logging

**Run the example:**
```bash
uv run python src/ragas_evaluation/with_mlflows/manual_logging.py
```

**Expected output:**
```
Step 1: Loading configuration...
✓ MLflow tracking URI: sqlite:///mlflow.db

Step 2: Loading evaluation dataset...
Loading evaluation dataset from: /path/to/evaluation_dataset.json
✓ Loaded 6 evaluation examples

Step 3: Configuring Zhipu AI backend...
✓ Configured Zhipu AI backend for RAGas evaluation: glm-5
  Temperature: 0.2 (low for consistent evaluation)
  Embeddings: embedding-3

Step 4: Creating RAGas evaluation...
✓ Created RAGas evaluation with metrics:
  - faithfulness
  - answer_relevancy
  - context_precision
  - context_recall
  - answer_correctness

Step 5: Setting up MLflow experiment...
✓ Using MLflow experiment: ragas-manual-logging

Step 6: Running RAGas evaluation independently...
✓ Evaluation complete!

Step 7: Logging results to MLflow manually...
✓ Logged 5 parameters
✓ Logged 5 metrics
✓ Logged dataset artifact: /path/to/evaluation_dataset.json
✓ Set 3 custom tags

MLflow Run Information:
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field                 ┃ Value                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ Run ID                │ xyz789abc012          │
│ Experiment            │ ragas-manual-logging  │
│ Status                │ COMPLETED             │
└───────────────────────┴──────────────────────┘

View results in MLflow UI: http://localhost:5000/#/runs/xyz789abc012

╭─────────────────────────────────────────────────────────────────╮
│ SCREENSHOT CHECKPOINTS                                         │
├─────────────────────────────────────────────────────────────────┤
│ 1. Open MLflow UI at http://localhost:5000                      │
│ 2. Navigate to Experiments → ragas-manual-logging               │
│ 3. Click on the latest run                                      │
│ 4. Take screenshot of custom parameters view                    │
│ 5. Suggested filename: mlflow_manual_logging_params.png         │
│ 6. Take screenshot of logged metrics                            │
│ 7. Suggested filename: mlflow_manual_logging_metrics.png        │
│ 8. Take screenshot of tag information                           │
│ 9. Suggested filename: mlflow_manual_logging_tags.png           │
│                                                                 │
│ Capture: Custom parameters, metrics table, and tags             │
╰─────────────────────────────────────────────────────────────────╯

╭─────────────────────────────────────────────────────────────────╮
│ COMPARISON WITH AUTO-LOGGING                                   │
├─────────────────────────────────────────────────────────────────┤
│ Manual Logging Advantages:                                     │
│ • Fine-grained control over what gets logged                    │
│ • Custom parameter names and values                             │
│ • Custom tags for better organization                           │
│ • Selective metric logging                                      │
│ • Additional artifacts and metadata                             │
│                                                                 │
│ Auto-Logging Advantages:                                        │
│ • Simpler implementation (one-line)                             │
│ • Automatic parameter capture                                   │
│ • Standardized format                                           │
│ • Less code to maintain                                         │
│                                                                 │
│ Use manual logging when you need customization.                 │
│ Use auto-logging for quick, standard evaluation logging.        │
╰─────────────────────────────────────────────────────────────────╯

Manual Logging Summary
• Dataset size: 6 examples
• Parameters logged: 5
• Metrics logged: 5
• Custom tags: 3
• Run ID: xyz789abc012
• Experiment: ragas-manual-logging
• Logging method: Manual
```

**Key MLflow APIs:**
```python
import mlflow

# Start run manually
with mlflow.start_run() as run:
    run_id = run.info.run_id

    # Log parameters manually
    mlflow.log_params({
        "model": "glm-5",
        "temperature": "0.2",
        "num_samples": "6",
        "metrics": "faithfulness,answer_relevancy,context_precision",
        "backend": "zhipu",
        "logging_method": "manual",
    })

    # Log metrics manually
    mlflow.log_metrics({
        "faithfulness": 0.85,
        "answer_relevancy": 0.92,
        "context_precision": 0.78,
        "context_recall": 0.83,
        "answer_correctness": 0.79,
    })

    # Log artifacts
    mlflow.log_artifact("/path/to/evaluation_dataset.json")

    # Set custom tags
    mlflow.set_tags({
        "evaluation_type": "ragas",
        "backend": "zhipu",
        "domain": "tax_evaluation",
        "logging_method": "manual",
    })
```

**Screenshot checkpoints:**
1. **Custom Parameters View**: Show manually logged parameters
   - Navigate to: Experiments → ragas-manual-logging → latest run → Parameters
   - Filename: `mlflow_manual_logging_params.png`

2. **Logged Metrics View**: Show manually logged metrics
   - Click on "Metrics" tab
   - Filename: `mlflow_manual_logging_metrics.png`

3. **Tags Information**: Show custom tags
   - Click on "Tags" section
   - Filename: `mlflow_manual_logging_tags.png`

4. **Artifacts View**: Show logged dataset artifact
   - Click on "Artifacts" tab
   - Filename: `mlflow_manual_logging_artifacts.png`

5. **Comparison View**: Compare auto vs manual logging runs
   - Select both runs in experiments list
   - Click "Compare"
   - Filename: `mlflow_auto_vs_manual_comparison.png`

**Real-World Use Cases:**
- **Custom experiments**: Non-standard evaluation workflows
- **Production monitoring**: Custom metrics and parameters
- **Multi-stage pipelines**: Logging intermediate results
- **Compliance audits**: Detailed logging for requirements

**Key concepts learned:**
- **Manual control**: Fine-grained logging control
- **Custom metadata**: Tags and parameters for organization
- **Artifact management**: Storing datasets and models
- **Workflow flexibility**: Adapting to specific needs

---

## MLflow UI Navigation Guide

### Viewing Experiments and Runs

1. **Open MLflow UI**:
   ```bash
   uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
   ```
   Then navigate to: http://localhost:5000

2. **View Experiments**:
   - Click on "Experiments" in left sidebar
   - See list of experiments: `ragas-auto-logging`, `ragas-manual-logging`

3. **View Runs**:
   - Click on an experiment name
   - See list of runs with timestamps and metrics

4. **View Run Details**:
   - Click on a specific run
   - See parameters, metrics, tags, and artifacts

### Comparing Runs

1. **Select Multiple Runs**:
   - Check boxes next to runs in experiments list
   - Click "Compare" button

2. **View Comparison**:
   - See side-by-side parameter comparison
   - See metric comparison charts
   - Identify differences and trends

### Accessing Artifacts

1. **Navigate to Run**:
   - Click on specific run

2. **View Artifacts**:
   - Click "Artifacts" tab
   - Download datasets, models, or other files

---

## Troubleshooting

### Issue: MLflow UI Not Showing Runs

**Symptoms:** MLflow UI opens but no experiments or runs appear

**Solutions:**
1. Check tracking URI matches: `sqlite:///mlflow.db`
2. Verify MLflow UI is using correct backend store
3. Restart MLflow UI with correct URI
4. Check file permissions on `mlflow.db`

---

### Issue: Metrics Not Logged

**Symptoms:** Run appears but metrics are missing

**Solutions:**
1. Check evaluation completed successfully
2. Verify metric names match ragas output
3. Look for errors in console output
4. Check MLflow server logs

---

### Issue: Artifacts Not Found

**Symptoms:** Artifact links are broken

**Solutions:**
1. Verify artifact paths are correct
2. Check file permissions
3. Ensure artifacts exist before logging
4. Use absolute paths for artifacts

---

### Issue: Runs Not Grouped in Experiments

**Symptoms:** Runs appear in "Default" experiment

**Solutions:**
1. Verify `mlflow.set_experiment()` is called
2. Check experiment name spelling
3. Ensure experiment is created before logging
4. Use consistent experiment names

---

## Real-World Use Cases

### 1. Experiment Tracking Pipeline

**Scenario:** Tracking RAG system improvements over time.

**Implementation:**
- Create separate experiments for each approach
- Run `auto_logging.py` after each change
- Compare runs to identify improvements
- Document successful strategies

**Benefits:**
- Systematic improvement tracking
- Data-driven decisions
- Reproducible experiments

---

### 2. A/B Testing Framework

**Scenario:** Comparing retrieval strategies in production.

**Implementation:**
- Use `manual_logging.py` for custom metrics
- Add tags for strategy identification
- Compare runs with different strategies
- Select best performing approach

**Benefits:**
- Objective comparison
- Quantitative decision making
- Historical record

---

### 3. Quality Monitoring Dashboard

**Scenario:** Continuous monitoring of production quality.

**Implementation:**
- Schedule regular evaluation runs
- Use consistent experiment naming
- Track metric trends in MLflow UI
- Set up alerts for degradation

**Benefits:**
- Early issue detection
- Quality visibility
- Trend analysis

---

### 4. Model Selection Process

**Scenario:** Choosing between different LLMs.

**Implementation:**
- Create experiment for each model
- Run evaluation with each model
- Compare metrics and costs
- Make informed selection

**Benefits:**
- Objective model comparison
- Cost-benefit analysis
- Performance baselines

---

### 5. Compliance and Auditing

**Scenario:** Meeting regulatory requirements for AI systems.

**Implementation:**
- Use `manual_logging.py` for detailed logging
- Log all parameters and datasets
- Add tags for compliance tracking
- Maintain historical record

**Benefits:**
- Audit trail
- Reproducibility
- Compliance documentation

---

## Key Concepts Learned

### MLflow Integration

1. **Experiment Organization**: Grouping related runs
2. **Parameter Tracking**: Recording configuration
3. **Metric Logging**: Tracking evaluation results
4. **Artifact Storage**: Saving datasets and models
5. **Custom Tags**: Organizing experiments

### Automatic vs Manual Logging

1. **Trade-offs**: Simplicity vs control
2. **Use Cases**: When to use each approach
3. **Best Practices**: Guidelines for selection
4. **Flexibility**: Adapting to needs

### Production Considerations

1. **Experiment Naming**: Consistent conventions
2. **Tagging Strategy**: Organizational scheme
3. **Artifact Management**: Storage and cleanup
4. **Monitoring**: Continuous evaluation

---

## Next Steps

After mastering MLflow integration:

1. **Advanced MLflow**: Explore model registry and deployment
2. **Custom Metrics**: Implement domain-specific metrics
3. **Automation**: CI/CD integration
4. **Monitoring**: Real-time quality dashboards
5. **Scaling**: Distributed evaluation pipelines

---

## Additional Resources

- **MLflow Documentation**: https://mlflow.org/docs/
- **MLflow Tracking**: https://mlflow.org/docs/latest/tracking.html
- **RAGas Documentation**: https://docs.ragas.io/
- **Project README**: `/home/an/projects/tracing_project/README.md`
- **Basics README**: `src/ragas_evaluation/basics/README.md`
