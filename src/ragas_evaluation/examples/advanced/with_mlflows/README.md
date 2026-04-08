# Advanced RAGas Examples with MLflow Integration

This directory provides MLflow-integrated versions of all advanced RAGas evaluation examples, enabling comprehensive experiment tracking, historical comparison, and reproducibility for production-level RAG system optimization.

## Overview

The MLflow-integrated advanced examples build upon the base advanced examples by adding comprehensive experiment tracking. Each example uses MLflow's nested run functionality to organize complex experiments with parent and child runs, making it easy to compare strategies, models, and metrics over time.

### What You'll Learn

- **Chunking Strategy Comparison with MLflow**: Track chunking experiments with nested runs for each strategy
- **Enhanced Model Comparison**: Comprehensive model evaluation with latency, token usage, and cost tracking
- **Custom Metrics with MLflow**: Track custom metric performance over time with historical analysis
- **Test Data Generation with MLflow**: Reproducible dataset generation with artifact logging and quality metrics

## Comparison: Standard vs MLflow-Integrated Examples

| Aspect | Standard Examples | MLflow-Integrated Examples |
|--------|------------------|----------------------------|
| **Experiment Tracking** | Manual notes | Automatic MLflow runs |
| **Historical Comparison** | Difficult | Built-in comparison UI |
| **Reproducibility** | Manual documentation | Automatic parameter logging |
| **Artifact Storage** | Manual file management | MLflow artifact repository |
| **Metric Visualization** | Console output | MLflow charts and graphs |
| **Run Organization** | Flat structure | Parent/nested runs |
| **Collaboration** | Share screenshots | Share MLflow server URL |
| **Production Ready** | Limited | Enterprise-grade tracking |

**When to use Standard Examples:**
- Learning the basics of RAGas evaluation
- Quick experimentation without tracking
- Local development without MLflow server
- Understanding evaluation patterns

**When to use MLflow-Integrated Examples:**
- Production RAG system optimization
- A/B testing different strategies
- Historical performance tracking
- Team collaboration and sharing
- Compliance and audit requirements
- Continuous monitoring

## Prerequisites

Before running these examples, ensure you have:

1. **Completed the basic advanced examples** - Familiarity with advanced patterns is assumed
2. **Set up your API key** in `.env` file:
   ```bash
   ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

3. **Start MLflow UI** (required for viewing results):
   ```bash
   uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
   ```

   Then open: http://localhost:5000

4. **Install dependencies** (if needed):
   ```bash
   uv sync --all-extras --dev
   ```

## Examples

### 1. Chunking Strategy Comparison with MLflow (`compare_chunking_strategies_with_mlflow.py`)

**Overview:** MLflow-integrated chunking strategy comparison with nested runs for each strategy.

**What it demonstrates:**
- Parent run for overall comparison
- Nested runs for each chunking strategy (small, medium, large)
- Parameter logging (chunk_size, overlap, num_chunks)
- Metric logging (context_precision, context_recall, retrieval_latency)
- MLflow comparison table generation

**Run the example:**
```bash
uv run python src/ragas_evaluation/examples/advanced/with_mlflows/compare_chunking_strategies_with_mlflow.py
```

**Expected output:**
```
[PARENT RUN] Starting chunking strategy comparison
Parent run ID: parent_abc123

Testing strategy: small_chunks (size=200, overlap=25)
  [NESTED RUN] Run ID: nested_def456
  Created 15 chunks
  Average chunk length: 198.5 characters
  Retrieval latency: 0.45s

Testing strategy: medium_chunks (size=500, overlap=50)
  [NESTED RUN] Run ID: nested_ghi789
  Created 8 chunks
  Average chunk length: 492.3 characters
  Retrieval latency: 0.32s

Testing strategy: large_chunks (size=1000, overlap=100)
  [NESTED RUN] Run ID: nested_jkl012
  Created 4 chunks
  Average chunk length: 985.7 characters
  Retrieval latency: 0.28s

MLflow Comparison Table:
View at: http://localhost:5000/#/experiments/1
```

**Key MLflow APIs:**
```python
import mlflow

# Start parent run
with mlflow.start_run(run_name="chunking_comparison_parent") as parent_run:
    parent_run_id = parent_run.info.run_id

    # Log parent parameters
    mlflow.log_param("num_strategies", str(len(strategies)))

    # Start nested runs for each strategy
    with mlflow.start_run(nested=True, run_name=run_name) as run:
        # Log strategy-specific parameters and metrics
        mlflow.log_param("strategy_name", strategy_name)
        mlflow.log_param("chunk_size", str(chunk_size))
        mlflow.log_metric("num_chunks", num_chunks)
        mlflow.log_metric("retrieval_latency", retrieval_latency)
```

**Screenshot checkpoints:**
1. **MLflow Experiments View**: Show parent run with nested children
   - Navigate to: Experiments → ragas_chunking_comparison
   - Filename: `mlflow_chunking_experiments.png`

2. **Nested Runs View**: Show expanded parent run with children
   - Click on parent run to expand
   - Filename: `mlflow_chunking_nested_runs.png`

3. **Comparison Table**: Show side-by-side metrics comparison
   - Select all nested runs → Click Compare
   - Filename: `mlflow_chunking_comparison.png`

**Real-World Use Cases:**
- **Production Optimization**: Track chunking experiments over time
- **Performance Regression**: Detect when changes affect retrieval quality
- **Capacity Planning**: Analyze latency trends across different chunk sizes
- **Documentation**: Maintain auditable record of optimization decisions

---

### 2. Enhanced Model Comparison with MLflow (`compare_models_enhanced_with_mlflow.py`)

**Overview:** Enhanced model comparison with comprehensive MLflow tracking including latency, token usage, and cost metrics.

**What it demonstrates:**
- Parent run for overall model comparison
- Nested runs for each model evaluated
- Per-query latency tracking
- Token usage estimation
- Cost-benefit analysis with MLflow logging

**Run the example:**
```bash
uv run python src/ragas_evaluation/examples/advanced/with_mlflows/compare_models_enhanced_with_mlflow.py
```

**Expected output:**
```
[PARENT RUN] Starting model comparison
Parent run ID: parent_xyz789

Evaluating model: glm-5
  [NESTED RUN] Run ID: nested_abc123
  Average latency: 1.52s
  Total tokens: 1250
  Faithfulness: 0.85

Evaluating model: glm-4
  [NESTED RUN] Run ID: nested_def456
  Average latency: 1.18s
  Total tokens: 1100
  Faithfulness: 0.80

Cost-Benefit Analysis:
• Best Quality: glm-5 (faithfulness: 0.85)
• Fastest: glm-4 (latency: 1.18s)
• Best Value: glm-4 (quality/cost: 28.33)
```

**Key MLflow APIs:**
```python
import mlflow

# Enhanced metric logging
with mlflow.start_run(nested=True, run_name=run_name) as run:
    # Log standard metrics
    mlflow.log_metric("avg_latency", avg_latency)
    mlflow.log_metric("total_tokens", total_tokens)
    mlflow.log_metric("cost_per_1k_tokens", cost_per_1k)

    # Log per-query latencies
    for i, latency in enumerate(latencies):
        mlflow.log_metric(f"query_{i}_latency", latency)

    # Log RAGas metrics
    for metric_name, value in metrics.items():
        mlflow.log_metric(f"ragas_{metric_name}", value)
```

**Screenshot checkpoints:**
1. **Model Comparison Chart**: Show metrics across models
   - Select all model runs → Compare → Charts
   - Filename: `mlflow_model_comparison_charts.png`

2. **Latency Analysis**: Show per-query latency trends
   - Metrics tab → query_*_latency
   - Filename: `mlflow_model_latency_analysis.png`

3. **Cost Comparison**: Show cost vs quality scatter plot
   - Charts → Configure → X: cost_per_1k_tokens, Y: ragas_faithfulness
   - Filename: `mlflow_model_cost_quality.png`

**Real-World Use Cases:**
- **Model Selection**: Data-driven model choice with historical tracking
- **Cost Optimization**: Track token usage and costs over time
- **Performance SLAs**: Monitor latency metrics for compliance
- **Vendor Comparison**: Compare different LLM providers objectively

---

### 3. Custom Metrics with MLflow (`custom_metrics_with_mlflow.py`)

**Overview:** Custom metrics demonstration with MLflow tracking for historical performance analysis.

**What it demonstrates:**
- Simple custom metric (citation accuracy) with MLflow logging
- Complex composite metric with component score tracking
- Domain-specific metrics with tagging
- Historical performance analysis capabilities

**Run the example:**
```bash
uv run python src/ragas_evaluation/examples/advanced/with_mlflows/custom_metrics_with_mlflow.py
```

**Expected output:**
```
[PARENT RUN] Starting custom metrics demonstration
Parent run ID: parent_custom_123

Demonstrating Simple Custom Metric: Citation Accuracy
  [NESTED RUN] Run ID: citation_run_123
  Citation Accuracy: 1.00
  Logged to MLflow: custom_citation_accuracy = 1.00

Demonstrating Complex Composite Metric
  [NESTED RUN] Run ID: composite_run_456
  Composite Score: 0.85
  Components: faithfulness(0.4) + relevancy(0.3) + citation(0.3)

Domain-Specific Examples:
• Legal: Case Law Citation (score: 0.95)
• Medical: Treatment Protocol Adherence (score: 0.88)
• Financial: Regulatory Compliance (score: 0.92)
```

**Key MLflow APIs:**
```python
import mlflow

# Custom metric logging
def log_custom_metric_to_mlflow(metric_name, score, components=None, tags=None):
    # Log main metric with custom_ prefix
    mlflow.log_metric(f"custom_{metric_name}", score)

    # Log component scores
    if components:
        for component_name, component_value in components.items():
            mlflow.log_metric(f"custom_{metric_name}_{component_name}", component_value)

    # Set tags for filtering
    if tags:
        mlflow.set_tags(tags)
```

**Screenshot checkpoints:**
1. **Custom Metrics View**: Show custom metrics in MLflow
   - Metrics tab → custom_* metrics
   - Filename: `mlflow_custom_metrics_view.png`

2. **Metric Trends**: Show custom metric performance over time
   - Charts → Select custom_* metrics
   - Filename: `mlflow_custom_metric_trends.png`

3. **Domain Filtering**: Show domain-specific metric filtering
   - Tags → domain: legal/medical/financial
   - Filename: `mlflow_domain_metrics_filtered.png`

**Real-World Use Cases:**
- **Domain Adaptation**: Track domain-specific metric improvements
- **Metric Validation**: Correlate custom metrics with human evaluations
- **Regulatory Compliance**: Document custom metric performance over time
- **Business KPIs**: Track custom metrics aligned with business goals

---

### 4. Test Data Generation with MLflow (`test_data_generation_with_mlflow.py`)

**Overview:** Dataset generation with MLflow tracking for reproducibility and quality monitoring.

**What it demonstrates:**
- Synthetic data generation with parameter logging
- Golden dataset creation with artifact logging
- Data quality validation with metric tracking
- Reproducibility via random seed tracking

**Run the example:**
```bash
uv run python src/ragas_evaluation/examples/advanced/with_mlflows/test_data_generation_with_mlflow.py
```

**Expected output:**
```
[PARENT RUN] Starting test data generation
Parent run ID: parent_data_gen_456

Generating Synthetic Dataset
  [NESTED RUN] synthetic_generation
  Samples: 5
  Seed: 42
  Created 5 synthetic samples
  Logged parameters: num_samples=5, seed=42
  Logged artifact: synthetic_dataset.json

Creating Golden Dataset
  [NESTED RUN] golden_dataset_creation
  Documents: 3
  Created 3 golden samples
  Logged artifact: golden_dataset.json

Validating Dataset Quality
  Validation PASSED: 8/8 samples valid
  Logged metrics: valid_samples=8, avg_question_length=45.2
```

**Key MLflow APIs:**
```python
import mlflow

# Dataset generation logging
def log_dataset_generation_to_mlflow(
    dataset_type, dataset, file_path,
    generation_params, stats, validation_result
):
    with mlflow.start_run(nested=True, run_name=run_name) as run:
        # Log generation parameters
        mlflow.log_param("dataset_type", dataset_type)
        for key, value in generation_params.items():
            mlflow.log_param(key, str(value))

        # Log statistics as metrics
        mlflow.log_metric("total_samples", stats.total_samples)
        mlflow.log_metric("valid_samples", stats.valid_samples)
        mlflow.log_metric("generation_seed", stats.generation_seed)

        # Log validation results
        mlflow.log_metric("validation_passed", 1 if validation_result["valid"] else 0)

        # Log dataset as artifact
        mlflow.log_artifact(str(file_path))
```

**Screenshot checkpoints:**
1. **Dataset Artifacts**: Show logged dataset files
   - Artifacts tab → synthetic_dataset.json, golden_dataset.json
   - Filename: `mlflow_dataset_artifacts.png`

2. **Generation Parameters**: Show reproducibility parameters
   - Parameters tab → num_samples, seed, corpus_size
   - Filename: `mlflow_dataset_parameters.png`

3. **Quality Metrics**: Show dataset quality over time
   - Charts → valid_samples, avg_question_length
   - Filename: `mlflow_dataset_quality_trends.png`

**Real-World Use Cases:**
- **Dataset Versioning**: Track all dataset versions in one place
- **Quality Monitoring**: Monitor dataset quality metrics over time
- **Reproducibility**: Ensure experiments can be reproduced exactly
- **Compliance**: Maintain audit trail of dataset generation

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
   - See list: `ragas_chunking_comparison`, `ragas_model_comparison_enhanced`,
     `ragas_custom_metrics`, `ragas_data_generation`

3. **View Parent/Nested Runs**:
   - Click on an experiment name
   - Click on parent run to see nested child runs
   - Expand/collapse nested runs for navigation

### Comparing Runs

1. **Select Multiple Runs**:
   - Check boxes next to runs in experiments list
   - Click "Compare" button

2. **View Comparison**:
   - See side-by-side parameter comparison
   - See metric comparison charts
   - Identify differences and trends

3. **Chart Customization**:
   - Click "Charts" tab in comparison view
   - Select metrics to plot
   - Customize chart types (line, bar, scatter)

### Accessing Artifacts

1. **Navigate to Run**:
   - Click on specific run (parent or nested)

2. **View Artifacts**:
   - Click "Artifacts" tab
   - Download datasets, models, or other files
   - View artifact metadata

### Filtering and Searching

1. **Filter by Tags**:
   - Use tag filters to find specific runs
   - Examples: domain="legal", metric_type="composite"

2. **Search Parameters**:
   - Use parameter search to find runs with specific configs
   - Examples: chunk_size=500, model=glm-5

---

## Troubleshooting

### Issue: Nested Runs Not Appearing

**Symptoms:** Parent run appears but nested runs are missing

**Solutions:**
1. Verify nested=True is used when starting child runs
2. Check that parent run context is active when starting children
3. Refresh MLflow UI to update run hierarchy
4. Check experiment for all runs (may be in different views)

---

### Issue: Metrics Not Logged

**Symptoms:** Runs appear but custom metrics are missing

**Solutions:**
1. Check metric names don't contain invalid characters
2. Ensure metrics are numeric (int/float)
3. Verify mlflow.log_metric() is called within active run
4. Check for exceptions in logging code

---

### Issue: Artifacts Not Found

**Symptoms:** Artifact links are broken or files missing

**Solutions:**
1. Verify file paths are absolute
2. Check files exist before logging
3. Ensure MLflow has permission to read files
4. Use temp directories with proper permissions

---

### Issue: Experiment Names Colliding

**Symptoms:** Runs appearing in wrong experiments

**Solutions:**
1. Use unique experiment names for different purposes
2. Check mlflow.set_experiment() is called correctly
3. Verify experiment name spelling
4. Create separate experiments for different projects

---

## Real-World Use Cases

### 1. Production RAG System Optimization

**Scenario:** Systematically optimizing a production RAG system.

**Implementation:**
1. Run chunking comparison with MLflow tracking
2. Run model comparison with MLflow tracking
3. Track custom metrics for domain-specific quality
4. Generate golden datasets with MLflow logging
5. Compare all experiments in MLflow UI
6. Make data-driven optimization decisions

**Benefits:**
- Complete audit trail of all experiments
- Easy comparison across different strategies
- Reproducible experiments with logged parameters
- Historical context for decision making

---

### 2. Continuous Quality Monitoring

**Scenario:** Monitoring RAG system quality in production.

**Implementation:**
1. Schedule regular evaluation runs with MLflow
2. Track metrics over time in MLflow charts
3. Set up alerts for metric degradation
4. Compare current performance to baselines
5. Use tags to organize runs by deployment

**Benefits:**
- Early detection of quality issues
- Historical trend analysis
- Evidence-based capacity planning
- Compliance documentation

---

### 3. A/B Testing Framework

**Scenario:** Testing new retrieval strategies in production.

**Implementation:**
1. Create MLflow experiment for A/B test
2. Log control and variant runs with tags
3. Use nested runs for multiple test iterations
4. Compare results in MLflow UI
5. Deploy winner based on statistical significance

**Benefits:**
- Risk-free experimentation
- Quantified improvement metrics
- Historical record of all tests
- Easy rollback documentation

---

### 4. Team Collaboration

**Scenario:** Multiple team members working on RAG optimization.

**Implementation:**
1. Central MLflow server for team access
2. Consistent experiment naming conventions
3. Use tags to organize by team member/feature
4. Share MLflow URLs for collaboration
5. Review runs in team meetings

**Benefits:**
- Shared experiment repository
- Easy knowledge sharing
- Reduced duplicate work
- Team-wide visibility

---

### 5. Compliance and Auditing

**Scenario:** Meeting regulatory requirements for AI systems.

**Implementation:**
1. Use manual logging for detailed tracking
2. Log all parameters, datasets, and metrics
3. Add tags for compliance tracking
4. Maintain historical record in MLflow
5. Generate audit reports from MLflow data

**Benefits:**
- Complete audit trail
- Reproducible experiments
- Compliance documentation
- Easy regulator access

---

## Key Concepts Learned

### MLflow Integration Patterns

1. **Parent/Nested Runs**: Organize complex experiments hierarchically
2. **Parameter Logging**: Track all configuration for reproducibility
3. **Metric Logging**: Record all evaluation metrics
4. **Artifact Storage**: Save datasets and models
5. **Tagging**: Organize experiments with metadata

### Advanced Experimentation

1. **Chunking Optimization**: Systematic strategy comparison
2. **Model Selection**: Comprehensive evaluation with cost tracking
3. **Custom Metrics**: Domain-specific evaluation with tracking
4. **Data Generation**: Reproducible dataset creation

### Production Considerations

1. **Experiment Organization**: Consistent naming and tagging
2. **Collaboration**: Shared MLflow server access
3. **Monitoring**: Continuous evaluation tracking
4. **Compliance**: Detailed logging for audits

---

## Next Steps

After mastering MLflow-integrated advanced examples:

1. **MLflow Model Registry**: Deploy and version RAG models
2. **Automation**: CI/CD integration for evaluation pipelines
3. **Dashboards**: Build custom MLflow dashboards
4. **Alerting**: Set up metric degradation alerts
5. **Scaling**: Distributed evaluation with MLflow

---

## Additional Resources

- **MLflow Documentation**: https://mlflow.org/docs/
- **MLflow Tracking**: https://mlflow.org/docs/latest/tracking.html
- **RAGas Documentation**: https://docs.ragas.io/
- **Base Advanced Examples**: `@src/ragas_evaluation/examples/advanced/README.md`
- **MLflow Integration Basics**: `@src/ragas_evaluation/with_mlflows/README.md`
- **Project README**: `@README.md`
