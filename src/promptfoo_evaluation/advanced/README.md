# Promptfoo Advanced Examples

This directory contains advanced promptfoo examples demonstrating RAG evaluation, MLflow integration, and production-ready testing patterns.

## Prerequisites

Before running these examples, ensure you have:

1. **Set up your API key** in `.env` file:
   ```bash
   ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

2. **Install promptfoo**:
   ```bash
   npm install -g promptfoo
   # or use npx
   ```

3. **Install Python dependencies**:
   ```bash
   uv sync --all-extras --dev
   ```

4. **Start MLflow UI** (for MLflow integration examples):
   ```bash
   uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
   ```

   Then open: http://localhost:5000

---

## Examples

### 1. RAG Basics (`rag_basics.yaml`)

**Overview:** RAG evaluation with static context and quality assertions.

**What it demonstrates:**
- Static context-based RAG testing
- Context recall, relevance, and faithfulness assertions
- Tax law domain evaluation
- Answer quality measurement

**Run the example:**
```bash
npx promptfoo eval -c rag_basics.yaml
npx promptfoo view
```

**Key Assertion Types:**

| Assertion | Description | Use Case |
|-----------|-------------|----------|
| `context-recall` | Measures context usage | Did the model use retrieved info? |
| `context-faithfulness` | Checks grounding in context | Did it hallucinate? |
| `answer-relevance` | Scores answer relevance | Is the answer on-topic? |

**Example Configuration:**

```yaml
tests:
  - vars:
      question: "What is taxable income?"
      context: "Taxable income = assessable income - deductions"
    assert:
      - type: context-recall
        threshold: 0.7
      - type: context-faithfulness
        threshold: 0.6
      - type: answer-relevance
        threshold: 0.7
```

**Real-World Use Cases:**
- **RAG System Testing**: Validate retrieval-augmented generation quality
- **Context Evaluation**: Measure how well models use retrieved context
- **Hallucination Detection**: Identify unsupported claims
- **Answer Quality**: Ensure responses meet quality standards

---

### 2. RAG Evaluation (`rag_evaluation.yaml`)

**Overview:** RAG evaluation with custom Python provider integration.

**What it demonstrates:**
- Custom provider pattern for RAG assertions
- Integration with VectorStore infrastructure
- Dynamic retrieval simulation
- Domain-specific assertion functions

**Run the example:**
```bash
npx promptfoo eval -c rag_evaluation.yaml
```

**Custom Provider Integration:**

```yaml
providers:
  - id: rag_provider
    config:
      type: python
      path: ../../shared/providers/rag_provider.py
      function: get_assertion_output
```

The custom provider (`shared/providers/rag_provider.py`) provides:

```python
def get_assertion_output(prompt: str, context: dict) -> dict:
    """Evaluate RAG assertions."""
    output = context.get("output", "")

    # Domain-specific validation
    if "tax" in prompt.lower():
        return contains_tax_keywords(output)

    return {"pass": True, "score": 1.0}
```

**Architecture:**

```
┌─────────────────┐
│  Promptfoo      │
│  Evaluation     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Custom RAG Provider        │
│  - VectorStore integration   │
│  - RetrievalChain usage      │
│  - Domain assertions         │
└─────────────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  RAG Infrastructure          │
│  - VectorStore              │
│  - RetrievalChain           │
│  - Tax law documents         │
└─────────────────────────────┘
```

**Real-World Use Cases:**
- **Dynamic RAG Testing**: Test with real retrieval systems
- **Custom Assertions**: Domain-specific validation logic
- **Production RAG**: Validate before deployment
- **A/B Testing**: Compare retrieval strategies

---

### 3. RAG Comparison (`rag_comparison.yaml`)

**Overview:** Compare different RAG configurations.

**What it demonstrates:**
- Chunk size comparisons
- Top-k retrieval variations
- Strategy comparison
- Performance trade-offs

**Run the example:**
```bash
npx promptfoo eval -c rag_comparison.yaml
```

**Configuration Comparison:**

| Config | Chunk Size | Top-K | Expected Result |
|--------|-----------|-------|-----------------|
| small_chunks_top2 | 256 | 2 | Focused, may miss details |
| large_chunks_top2 | 1024 | 2 | More context per chunk |
| small_chunks_top4 | 256 | 4 | Better coverage |
| small_chunks_top5 | 256 | 5 | Maximum coverage, more noise |
| medium_chunks_top3 | 512 | 3 | Balanced approach |

**Expected Insights:**

```yaml
# Small chunks + higher top-k
- Better coverage
- More noise
- Higher latency

# Large chunks + lower top-k
- More focused
- May miss details
- Lower latency

# Medium chunks + mid top-k
- Balanced coverage
- Optimal for most use cases
```

**Real-World Use Cases:**
- **Configuration Tuning**: Find optimal chunk size and top-k
- **Performance Optimization**: Balance quality vs. speed
- **Production Decisions**: Evidence-based configuration choices
- **A/B Testing**: Compare retrieval strategies

---

### 4. MLflow Integration (`mlflow_integration.py`)

**Overview:** End-to-end MLflow integration for experiment tracking.

**What it demonstrates:**
- Running promptfoo from Python
- Parsing results and logging to MLflow
- Experiment management
- Artifact and metrics logging

**Run the example:**
```bash
# First, start MLflow UI
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000

# Then run the integration script
uv run python mlflow_integration.py
```

**Key Features:**

```python
# Run promptfoo evaluation
results = run_promptfoo_for_mlflow(config_path, output_path)

# Log to MLflow
run_id = log_rag_evaluation_to_mlflow(config_name, results)
```

**MLflow Experiment: `promptfoo-rag`**

Logged metrics:
- `pass_rate`: Percentage of passing tests
- `average_score`: Mean score across all tests
- `total_tokens`: Total tokens used
- `total_cost`: Total API cost
- `avg_latency_ms`: Average response latency

Logged artifacts:
- `results.json`: Full promptfoo results
- `summary.txt`: Human-readable summary

**MLflow UI View:**

```
Experiments
└── promptfoo-rag
    ├── rag_basics
    │   ├── Metrics: pass_rate, avg_score, cost
    │   └── Artifacts: results.json, summary.txt
    ├── rag_evaluation
    │   ├── Metrics: pass_rate, avg_score, cost
    │   └── Artifacts: results.json, summary.txt
    └── rag_comparison
        ├── Metrics: pass_rate, avg_score, cost
        └── Artifacts: results.json, summary.txt
```

**Real-World Use Cases:**
- **Experiment Tracking**: Track evaluation runs over time
- **Regression Testing**: Compare current vs. historical results
- **Performance Monitoring**: Track metrics across runs
- **Model Comparison**: Compare different GLM models
- **Cost Management**: Monitor API costs over time

---

## RAG Evaluation Architecture

### Components

```
┌──────────────────────────────────────────────────────┐
│                   Promptfoo CLI                       │
│  ┌────────────────────────────────────────────────┐ │
│  │  Test Configuration (YAML)                     │ │
│  │  - Prompts                                      │ │
│  │  - Providers                                    │ │
│  │  - Tests (with context)                         │ │
│  │  - Assertions                                   │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│              Custom RAG Provider                      │
│  - get_assertion_output(prompt, context)            │
│  - Domain-specific assertions                        │
│  - Integration with VectorStore/RetrievalChain       │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│            RAG Infrastructure (Existing)              │
│  ┌────────────────────────────────────────────────┐ │
│  │  VectorStore                                   │ │
│  │  - Document storage                            │ │
│  │  - Similarity search                           │ │
│  │  - Top-k retrieval                             │ │
│  └────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────┐ │
│  │  RetrievalChain                                │ │
│  │  - LCEL chain composition                      │ │
│  │  - Prompt formatting                           │ │
│  │  - Response generation                         │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│                  Test Data                            │
│  data/rag/australian_tax_law.txt                     │
└──────────────────────────────────────────────────────┘
```

---

## RAG Assertion Best Practices

### 1. Context Recall

Measure how much retrieved context is used:

```yaml
assert:
  - type: context-recall
    threshold: 0.7  # 70% of context should be utilized
```

### 2. Context Faithfulness

Ensure answers don't hallucinate:

```yaml
assert:
  - type: context-faithfulness
    threshold: 0.8  # 80% faithful to context
```

### 3. Answer Relevance

Score relevance to the question:

```yaml
assert:
  - type: answer-relevance
    threshold: 0.6  # Moderately relevant
```

### 4. Combined Assertions

Use multiple assertions for comprehensive evaluation:

```yaml
assert:
  - type: context-recall
    threshold: 0.7
  - type: context-faithfulness
    threshold: 0.8
  - type: answer-relevance
    threshold: 0.6
  - type: python
    value: python_asserts
    function: validate_context_faithfulness
```

---

## MLflow Integration Patterns

### Pattern 1: Simple Logging

Log results to a single experiment:

```python
from promptfoo_evaluation.shared.mlflow_handler import log_promptfoo_run_to_mlflow

run_id = log_promptfoo_run_to_mlflow(
    results="eval_results.json",
    experiment_name="promptfoo-rag",
    run_name="basics_test"
)
```

### Pattern 2: Custom Metrics

Add custom metrics during logging:

```python
manager = MLflowExperimentManager("promptfoo-rag")
with manager.run_experiment() as run:
    # Log standard metrics
    manager.log_metrics(parser.get_metrics())

    # Log custom metrics
    manager.log_metrics({
        "context_utilization": 0.85,
        "hallucination_score": 0.05,
    })
```

### Pattern 3: Artifact Logging

Log additional artifacts for analysis:

```python
# Log comparison table
manager.log_artifact("comparison_table.csv")

# Log detailed results
manager.log_text(detailed_analysis, "analysis.txt")

# Log configuration
manager.log_artifact("config.yaml")
```

---

## Production Considerations

### Deployment Checklist

- [ ] **CI/CD Integration**: Automate evaluations in CI/CD pipeline
- [ ] **Regression Tests**: Run promptfoo tests on every change
- [ ] **Performance Baselines**: Establish and track baseline metrics
- [ ] **Alert Thresholds**: Set up alerts for metric degradation
- [ ] **Cost Monitoring**: Track and budget API costs
- [ ] **Artifact Storage**: Configure MLflow artifact storage for production

### Monitoring Metrics

Key metrics to monitor in production:

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| Pass Rate | Percentage of passing tests | < 90% |
| Avg Score | Mean test score | < 0.8 |
| Latency | Average response time | > 2000ms |
| Cost | Total API cost per run | > $X |
| Hallucination | Hallucination rate | > 5% |

### Continuous Evaluation

Schedule regular evaluations:

```bash
# Cron job for daily evaluation
0 2 * * * cd /app && uv run python mlflow_integration.py
```

---

## Troubleshooting

### Issue: Context not being used

**Symptoms**: Low context-recall scores

**Solutions:**
1. Check prompt explicitly references context
2. Verify context format matches expectations
3. Adjust top-k for better retrieval

### Issue: High hallucination rate

**Symptoms**: Low context-faithfulness scores

**Solutions:**
1. Improve context quality
2. Add explicit grounding instructions
3. Use faithfulness assertions

### Issue: MLflow artifacts not logging

**Symptoms**: Missing artifacts in MLflow UI

**Solutions:**
1. Check file paths are absolute
2. Verify MLflow tracking URI is set
3. Check write permissions

---

## Next Steps

After mastering these advanced examples:

1. **Production Deployment**:
   - Set up CI/CD integration
   - Configure monitoring and alerting
   - Establish performance baselines

2. **Custom Development**:
   - Build domain-specific RAG providers
   - Create custom assertion libraries
   - Integrate with existing testing frameworks

3. **Advanced Topics**:
   - Distributed evaluation at scale
   - Real-time monitoring dashboards
   - Automated regression detection
