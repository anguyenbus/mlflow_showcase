# Promptfoo Advanced Examples

This directory contains advanced promptfoo examples demonstrating comprehensive evaluation techniques including RAG evaluation, hallucination prevention, temperature optimization, and factuality scoring. All examples include MLflow integration for experiment tracking.

## Prerequisites

Before running these examples, ensure you have:

1. **Set up your API key** in `.env` file:
   ```bash
   ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

   Get your API key from: https://open.bigmodel.cn/

2. **Install promptfoo**:
   ```bash
   npm install -g promptfoo
   # or use npx (no installation required)
   ```

3. **Install Python dependencies**:
   ```bash
   uv sync --all-extras --dev
   ```

4. **Start MLflow UI** (optional, for experiment tracking):
   ```bash
   uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
   ```

   Then open: http://localhost:5000

---

## Quick Start

### Run All Advanced Evaluations

```bash
# Navigate to the advanced directory
cd src/promptfoo_evaluation/advanced

# Run all evaluations using the convenience script
python run_all_advanced.py

# Or run individual topics (see below)
```

---

## Topics

### 1. RAG Pipeline Evaluation (`rag_pipeline/`)

**Overview:** End-to-end testing of Retrieval-Augmented Generation systems with context quality assertions.

**What it tests:**
- Context relevance - Is retrieved context relevant to the question?
- Context faithfulness - Does the answer stay grounded in context?
- Context recall - How much of the context is actually used?
- Answer relevance - Is the response on-topic?

**Run the example:**
```bash
cd rag_pipeline
python rag_pipeline_test.py
# or
OPENAI_API_KEY=$ZHIPU_API_KEY npx promptfoo eval -c rag_pipeline.yaml
```

**Key Features:**
- 10 test scenarios covering good/insufficient/irrelevant context
- Numerical data verification (tax rates, dates)
- Multiple facts extraction
- MLflow experiment: `promptfoo-advanced-rag`

**[Full Documentation & Guide](rag_pipeline/README.md)**

---

### 2. Hallucination Prevention (`prevent_hallucination/`)

**Overview:** Detect and reduce hallucinations by testing LLM behavior on questions where it might be tempted to invent information.

**What it tests:**
- Future predictions - Model refuses to speculate about the future
- Non-existent entities - Model acknowledges when things don't exist
- Anachronisms - Model detects temporal impossibilities
- Obscure citations - Model doesn't fabricate study results

**Run the example:**
```bash
cd prevent_hallucination
python prevent_hallucination_test.py
# or
OPENAI_API_KEY=$ZHIPU_API_KEY npx promptfoo eval -c prevent_hallucination.yaml
```

**Key Features:**
- 10 hallucination-prone test scenarios
- Refusal rate tracking (higher is better for unanswerable questions)
- Factuality and attribution scoring
- MLflow experiment: `promptfoo-advanced-hallucination`

**[Full Documentation & Guide](prevent_hallucination/README.md)**

---

### 3. Temperature Optimization (`choosing_right_temperature/`)

**Overview:** Find optimal temperature settings for different task types by sweeping across temperature values.

**What it tests:**
- Temperature 0.0 - Most deterministic, consistent
- Temperature 0.3 - Low creativity, high reliability
- Temperature 0.7 - Balanced between consistency and creativity
- Temperature 1.0 - Most creative, highest variance

**Run the example:**
```bash
cd choosing_right_temperature
python temperature_test.py
# or
OPENAI_API_KEY=$ZHIPU_API_KEY npx promptfoo eval -c temperature_sweep.yaml
```

**Key Features:**
- 8 different task types (creative, factual, code, summary, etc.)
- Variance analysis across temperature values
- Task-specific temperature recommendations
- MLflow experiment: `promptfoo-advanced-temperature`

**[Full Documentation & Guide](choosing_right_temperature/README.md)**

---

### 4. Factuality Evaluation (`evaluating_factuality/`)

**Overview:** Score responses for factual accuracy against known ground truth across different information types.

**What it tests:**
- Dates - Historical events, time periods
- Numbers - Scientific constants, quantities
- Entities - Capital cities, people, places
- Relationships - Authorship, discoveries

**Run the example:**
```bash
cd evaluating_factuality
python factuality_test.py
# or
OPENAI_API_KEY=$ZHIPU_API_KEY npx promptfoo eval -c factuality.yaml
```

**Key Features:**
- 12 test cases with known correct answers
- Category-specific factuality breakdown
- Numerical precision verification
- MLflow experiment: `promptfoo-advanced-factuality`

**[Full Documentation & Guide](evaluating_factuality/README.md)**

---

## Comparison Table

| Topic | Test Cases | Key Metrics | Best For | MLflow Experiment |
|-------|-----------|-------------|----------|-------------------|
| **RAG Pipeline** | 10 | Context relevance, faithfulness, recall | RAG systems | `promptfoo-advanced-rag` |
| **Hallucination** | 10 | Refusal rate, hallucination rate | Accuracy-critical apps | `promptfoo-advanced-hallucination` |
| **Temperature** | 8 | Variance, pass rate by temp | Parameter tuning | `promptfoo-advanced-temperature` |
| **Factuality** | 12 | Overall factuality, extraction accuracy | Factual QA systems | `promptfoo-advanced-factuality` |

---

## MLflow Integration

All advanced topics log to MLflow with consistent experiment naming: `promptfoo-advanced-{topic}`

### Logged Metrics

Each experiment logs:

**Base Metrics:**
- `pass_rate` - Percentage of tests passing all assertions
- `average_score` - Mean score across all tests
- `total_tokens` - Total tokens used
- `total_cost` - API cost in USD
- `avg_latency_ms` - Average response time

**Topic-Specific Metrics:**
- RAG: `context_relevance_avg`, `context_faithfulness_avg`, `context_recall_avg`
- Hallucination: `refusal_rate`, `hallucination_rate`, `factuality_score`
- Temperature: `temp_0.0_pass_rate`, `temp_0.3_pass_rate`, etc.
- Factuality: `dates_accuracy`, `numbers_accuracy`, `entities_accuracy`

### Viewing MLflow Results

```bash
# Start MLflow UI
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000

# Open browser to http://localhost:5000

# Navigate to Experiments > promptfoo-advanced-*
```

---

## Common Patterns

### Pattern 1: Python Runner with MLflow

All advanced topics use the same pattern for MLflow integration:

```python
from promptfoo_evaluation.shared.mlflow_handler import (
    MLflowExperimentManager,
    PromptfooResultParser,
)

# Run promptfoo evaluation
results = run_promptfoo_eval(config_path)

# Parse results
parser = PromptfooResultParser(results)

# Calculate topic-specific metrics
topic_metrics = calculate_topic_metrics(results)

# Log to MLflow
manager = MLflowExperimentManager("promptfoo-advanced-topic")
with manager.run_experiment(run_name="topic-eval") as run:
    manager.log_metrics(parser.get_metrics())
    manager.log_metrics(topic_metrics)
    manager.log_artifact(results_path)
```

### Pattern 2: Custom Assertions

Each topic uses custom Python assertions for domain-specific validation:

```python
def assert_fn(output, context):
    """Domain-specific validation logic."""
    # Your validation logic here
    return {
        "pass": boolean_result,
        "score": 0.0_to_1.0,
        "reason": "Explanation of result"
    }
```

### Pattern 3: Rich Console Output

All runners use `rich` for formatted console output:

```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="Results")
table.add_column("Metric", style="cyan")
table.add_column("Score", style="green")
console.print(table)
```

---

## Choosing the Right Evaluation

| Use Case | Recommended Evaluation | Reason |
|----------|----------------------|--------|
| **Building a RAG system** | RAG Pipeline | Tests retrieval quality and context usage |
| **Medical/legal advice** | Hallucination Prevention | High cost of hallucinations |
| **Creative applications** | Temperature Optimization | Find right creativity level |
| **Knowledge bases** | Factuality Evaluation | Ensure accuracy of information |
| **General QA** | All topics | Comprehensive evaluation |
| **Production deployment** | All topics | Establish baseline metrics |

---

## Progressive Learning Path

```
Basics (../basics/)
    ↓
Intermediate (../intermediate/)
    ↓
Advanced Topics (this directory)
    ├── RAG Pipeline
    ├── Hallucination Prevention
    ├── Temperature Optimization
    └── Factuality Evaluation
```

**Recommended order:**
1. Start with RAG Pipeline if you're building a RAG system
2. Then Hallucination Prevention for accuracy-critical applications
3. Temperature Optimization for parameter tuning
4. Factuality Evaluation for factual QA systems

---

## Troubleshooting

### Issue: All tests failing

**Possible causes:**
1. ZHIPU_API_KEY not set correctly
2. Network connectivity issues
3. Model name incorrect

**Solution:**
```bash
# Check API key
echo $ZHIPU_API_KEY

# Test connection
curl -X POST https://open.bigmodel.cn/api/paas/v4/chat/completions \
  -H "Authorization: Bearer $ZHIPU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-5-flash","messages":[{"role":"user","content":"test"}]}'
```

### Issue: MLflow not logging

**Possible causes:**
1. MLflow not installed
2. Tracking URI not set
3. File permission issues

**Solution:**
```bash
# Check MLflow installation
uv run mlflow --version

# Set tracking URI explicitly
export MLFLOW_TRACKING_URI=sqlite:///mlflow.db

# Check file permissions
ls -la mlflow.db
```

### Issue: Test data not found

**Possible causes:**
1. Running from wrong directory
2. Relative path issues

**Solution:**
```bash
# Always run from the topic directory
cd src/promptfoo_evaluation/advanced/rag_pipeline
python rag_pipeline_test.py
```

---

## Next Steps

After mastering these advanced examples:

1. **Production Integration:**
   - Set up CI/CD integration with promptfoo
   - Configure automated regression testing
   - Establish performance baselines and alerting

2. **Custom Development:**
   - Build domain-specific test cases
   - Create custom assertion libraries
   - Integrate with existing testing frameworks

3. **Advanced Topics:**
   - Distributed evaluation at scale
   - Real-time monitoring dashboards
   - Automated model selection

---

## Related Resources

- [Promptfoo Documentation](https://promptfoo.dev/docs/)
- [MLflow Documentation](https://mlflow.org/docs/)
- [Zhipu AI API](https://open.bigmodel.cn/)
- [RAGAS Framework](https://docs.ragas.io/)

---

## Additional Advanced Examples

The advanced directory also contains these earlier examples:

- `rag_basics.yaml` - Basic RAG evaluation with static context
- `rag_evaluation.yaml` - RAG with custom Python provider
- `rag_comparison.yaml` - Comparing RAG configurations
- `mlflow_integration.py` - MLflow integration demo

See the earlier sections of this README for details on these examples.
