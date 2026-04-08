# RAGas Advanced Examples

This directory contains advanced examples demonstrating production-level RAGas evaluation patterns for Retrieval-Augmented Generation (RAG) systems.

## 📚 Complete Guide

**For a comprehensive tutorial with screenshots, see: [RAGAS_COMPLETE_GUIDE.md](RAGAS_COMPLETE_GUIDE.md)**

This guide includes:
- Detailed explanations of each advanced pattern
- 10 MLflow UI screenshots showing experiment tracking
- Step-by-step instructions for chunking, model comparison, custom metrics, and data generation

## Overview

The advanced examples build upon the basics and MLflow integration examples to show practical patterns used in production RAG systems. Each example is self-contained and demonstrates specific advanced techniques for evaluating RAG systems.

### What You'll Learn

- **Chunking Strategy Comparison**: How different chunk sizes affect retrieval quality and performance
- **Model Comparison**: Evaluating multiple LLM models with identical metrics for fair comparison
- **Custom Metrics**: Creating domain-specific metrics beyond the standard RAGas metrics
- **Test Data Generation**: Generating synthetic and golden datasets for evaluation
- **MLflow Integration**: Comprehensive experiment tracking with MLflow (see `with_mlflows/`)

### Standard vs MLflow-Integrated Examples

| Aspect | Standard Examples | MLflow-Integrated Examples |
|--------|------------------|----------------------------|
| **Location** | This directory (`*.py`) | `with_mlflows/*.py` |
| **Tracking** | Console output only | Full MLflow experiment tracking |
| **Reproducibility** | Manual notes | Automatic parameter logging |
| **Comparison** | Manual comparison | MLflow comparison UI |
| **Best For** | Learning patterns | Production optimization |

**Tip:** Start with standard examples to understand the patterns, then use MLflow-integrated versions for production workloads.

## Prerequisites

Before running these examples, ensure you have:

1. **Completed the basic examples** - Familiarity with RAGas fundamentals is assumed
2. **Set up your API key** in `.env` file:
   ```bash
   ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

3. **Install dependencies** (if needed):
   ```bash
   uv sync --all-extras --dev
   ```

4. **Review MLflow integration** - The model comparison example uses MLflow for tracking


1. **Completed the basic examples** - Familiarity with RAGas fundamentals is assumed
2. **Set up your API key** in `.env` file:
   ```bash
   ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

3. **Install dependencies** (if needed):
   ```bash
   uv sync --all-extras --dev
   ```

4. **Review MLflow integration** - The model comparison example uses MLflow for tracking

## Examples

### 1. Chunking Strategy Comparison (`compare_chunking_strategies.py`)

**Overview:** Demonstrates how document chunking strategies impact RAG system performance.

**What it demonstrates:**
- Comparing small (200), medium (500), and large (1000) character chunks
- Measuring retrieval latency for each strategy
- Evaluating impact on RAGas metrics
- Trade-off analysis between precision and performance

**Run the example:**
```bash
uv run python src/ragas_evaluation/examples/advanced/compare_chunking_strategies.py
```

**Expected output:**
```
Testing strategy: small_chunks (size=200, overlap=25)
  Created 10 chunks
  Average chunk length: 182.1 characters
  Retrieval latency: 0.30s

Testing strategy: medium_chunks (size=500, overlap=50)
  Created 5 chunks
  Average chunk length: 349.2 characters
  Retrieval latency: 0.20s

Testing strategy: large_chunks (size=1000, overlap=100)
  Created 3 chunks
  Average chunk length: 548.7 characters
  Retrieval latency: 0.16s

Trade-off Analysis:
• Fastest Retrieval: large (0.16s)
• Most Granular: small (10 chunks)
• Broadest Context: large (3 chunks)

[TODO: Add screenshot showing chunking strategy comparison results]
```

**Real-World Use Cases:**
- **Production Optimization**: Finding optimal chunk size for your documents
- **Performance Tuning**: Balancing retrieval quality vs latency
- **A/B Testing**: Comparing chunking strategies before deployment
- **Domain Adaptation**: Customizing chunk sizes for different document types

**Key Concepts Learned:**
- Smaller chunks provide more precise retrieval but increase latency
- Larger chunks reduce retrieval time but may include irrelevant information
- Optimal chunk size depends on document structure and use case

---

### 2. Model Comparison (`compare_models.py`)

**Overview:** Demonstrates comparing different LLM models using identical RAGas metrics.

**What it demonstrates:**
- Evaluating multiple models (glm-5, glm-4) with same metrics
- Capturing performance metrics (latency, token usage)
- MLflow integration for run comparison
- Cost-benefit trade-off analysis

**Run the example:**
```bash
uv run python src/ragas_evaluation/examples/advanced/compare_models.py
```

**Expected output:**
```
Evaluating model: glm-5
  Average latency: 1.52s
  Total tokens: 1250
  Faithfulness: 0.85

Evaluating model: glm-4
  Average latency: 1.18s
  Total tokens: 1100
  Faithfulness: 0.80

Cost-Benefit Analysis:
• Best Quality: glm-5 (faithfulness: 0.85)
• Fastest: glm-4 (latency: 1.18s)
• Most Cost-Effective: glm-4 ($0.03/1K tokens)

[TODO: Add screenshot showing MLflow comparison view]
```

**Real-World Use Cases:**
- **Model Selection**: Choosing the best model for your use case
- **Cost Optimization**: Balancing quality vs cost
- **Performance Benchmarking**: Establishing baseline metrics
- **Migration Planning**: Evaluating new models before switching

**Key Concepts Learned:**
- Use identical metrics across models for fair comparison
- Track both quality and performance metrics
- Consider cost-benefit trade-offs for production decisions

---

### 3. Custom Metrics (`custom_metrics.py`)

**Overview:** Demonstrates creating domain-specific custom metrics for RAG evaluation.

**What it demonstrates:**
- Simple custom metric (citation accuracy)
- Complex composite metric combining multiple scores
- Domain-specific examples (legal, medical, financial)
- Integration with standard RAGas evaluation workflow

**Run the example:**
```bash
uv run python src/ragas_evaluation/examples/advanced/custom_metrics.py
```

**Expected output:**
```
Simple Custom Metric: Citation Accuracy
Citation Accuracy Score: 0.47

Complex Composite Metric
Composite Quality Score: 0.75
  (40% faithfulness + 30% relevancy + 30% citation)

Domain-Specific Use Cases:
Legal Domain: Case Law Citation
  Score: 0.28

Medical Domain: Treatment Protocol Adherence
  Score: 0.43

Financial Domain: Regulatory Compliance
  Score: 0.46
```

**Real-World Use Cases:**
- **Legal Tech**: Ensuring proper case law citations
- **Medical AI**: Verifying treatment protocol adherence
- **Financial Services**: Checking regulatory compliance
- **Domain-Specific QA**: Any industry requiring specialized scoring

**Key Concepts Learned:**
- Start with built-in metrics, then add custom ones
- Custom metrics enable domain-specific evaluation
- Composite metrics combine multiple scores meaningfully
- Test custom metrics on golden datasets

---

### 4. Test Data Generation (`test_data_generation.py`)

**Overview:** Demonstrates generating test datasets for RAG evaluation.

**What it demonstrates:**
- Synthetic data generation using RAGAS patterns
- Golden dataset creation from existing documents
- Data quality validation checks
- Reproducibility patterns (random seeds)

**Run the example:**
```bash
uv run python src/ragas_evaluation/examples/advanced/test_data_generation.py
```

**Expected output:**
```
Generating Synthetic Dataset
  Created 5 synthetic samples

Creating Golden Dataset
  Created 3 golden samples

Validating Dataset Quality
  Validation PASSED: 8/8 samples valid

Dataset Comparison:
Synthetic vs Golden Datasets
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Type      ┃ Use Case                     ┃ Pros                          ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Synthetic │ Development, testing, rapid  │ Fast to generate, controlled  │
│           │ iteration                    │ variety                       │
│ Golden    │ Production evaluation,       │ Realistic, human-validated    │
│           │ benchmarking                 │ quality                       │
└───────────┴──────────────────────────────┴───────────────────────────────┘
```

**Real-World Use Cases:**
- **Development**: Rapid iteration with synthetic data
- **Production**: Golden datasets for reliable evaluation
- **Testing**: Validation checks before deployment
- **Regression Testing**: Consistent datasets over time

**Key Concepts Learned:**
- Use synthetic data for rapid development iteration
- Use golden datasets for production evaluation
- Always validate dataset quality
- Use random seeds for reproducibility

## Metric Interpretation Guidance

### Advanced-Specific Metrics

**Chunking Metrics:**
- Retrieval Latency: Time to fetch relevant chunks
- Chunk Count: Number of chunks created
- Avg Chunk Length: Typical size of chunks

**Model Comparison Metrics:**
- Token Usage: Total tokens consumed
- Cost per 1K Tokens: Estimated API cost
- Latency: Average response time

**Custom Metrics:**
- Citation Accuracy: Proper source citation
- Composite Quality: Weighted combination of metrics
- Domain-Specific Scores: Industry-specific measures

### Trade-off Analysis

When comparing strategies, consider:

| Factor | Questions to Ask |
|--------|------------------|
| Quality | Does the change improve RAGas scores? |
| Performance | Is latency acceptable? |
| Cost | What's the impact on token usage? |
| Complexity | Is the solution maintainable? |

## Troubleshooting

### Issue: Memory Errors with Large Datasets

**Symptoms:** Out of memory errors during evaluation

**Solutions:**
- Reduce dataset size for testing
- Process data in batches
- Use streaming evaluation for very large datasets

---

### Issue: Inconsistent Results Across Runs

**Symptoms:** Scores vary between identical runs

**Solutions:**
- Set random seeds for data generation
- Use fixed temperature for LLM calls
- Ensure consistent data preprocessing
- Check for non-deterministic operations

---

### Issue: Custom Metric Scores Unexpected

**Symptoms:** Custom metric returns unexpected values

**Solutions:**
- Test metric on known examples first
- Add debug logging to trace scoring logic
- Verify input data format matches expectations
- Compare against manual scoring for validation

---

### Issue: MLflow Logging Fails

**Symptoms:** Errors when logging to MLflow

**Solutions:**
- Check MLflow tracking server is running
- Verify experiment name is valid
- Ensure all metrics are numeric values
- Check file permissions for artifact storage

## Real-World Use Cases

### 1. Production RAG System Optimization

**Scenario:** Optimizing a production RAG system for customer support.

**Implementation:**
1. Run chunking comparison to find optimal chunk size
2. Compare models for quality vs cost trade-offs
3. Create custom metrics for domain-specific scoring
4. Generate golden dataset from real support tickets
5. Establish baseline metrics for monitoring

**Benefits:**
- Data-driven optimization decisions
- Documented trade-offs for stakeholders
- Reproducible evaluation process
- Continuous improvement capability

---

### 2. A/B Testing Framework

**Scenario:** Testing new retrieval strategies in production.

**Implementation:**
1. Create evaluation datasets from production queries
2. Run comparison tests for new vs current strategies
3. Use MLflow to track all experimental runs
4. Apply statistical significance testing
5. Roll out improvements based on metrics

**Benefits:**
- Risk-free experimentation
- Quantified improvement metrics
- Rollback capability
- Evidence-based decisions

---

### 3. Quality Monitoring Workflow

**Scenario:** Continuous monitoring of RAG system quality.

**Implementation:**
1. Schedule regular evaluation runs
2. Track metrics in MLflow over time
3. Set up alerts for metric degradation
4. Use custom metrics for business KPIs
5. Generate regular quality reports

**Benefits:**
- Early detection of quality issues
- Trend analysis for capacity planning
- Compliance documentation
- Stakeholder transparency

---

### 4. Domain-Specific Evaluation

**Scenario:** Evaluating RAG for specialized domains (legal, medical).

**Implementation:**
1. Create domain-specific custom metrics
2. Build golden dataset from domain experts
3. Train evaluators on domain criteria
4. Establish quality thresholds
5. Regular recalibration with human review

**Benefits:**
- Accurate domain-specific scoring
- Regulatory compliance support
- Expert review integration
- Industry-standard evaluation

## Key Concepts Learned

### Advanced Chunking Strategies

1. **Chunk Size Impact**: Directly affects retrieval precision and latency
2. **Overlap Strategy**: Balances context continuity vs redundancy
3. **Domain Adaptation**: Different document types need different strategies
4. **Performance Tuning**: Trade-offs between quality and speed

### Model Selection and Comparison

1. **Fair Comparison**: Use identical metrics and datasets
2. **Beyond Quality**: Consider latency, cost, and token usage
3. **Production Realities**: Best model may not be highest quality
4. **MLflow Integration**: Essential for tracking and comparison

### Custom Metrics Design

1. **Start Simple**: Begin with basic custom metrics
2. **Domain Knowledge**: Leverage expertise for scoring logic
3. **Validation**: Test against human-labeled data
4. **Composition**: Combine metrics for composite scores

### Data Generation Patterns

1. **Synthetic for Speed**: Rapid iteration during development
2. **Golden for Quality**: Production evaluation needs real data
3. **Reproducibility**: Seeds and versioning are critical
4. **Quality Validation**: Always validate before using

## Next Steps

After completing these advanced examples, explore:

1. **Production Deployment**: Integrate evaluation into CI/CD pipelines
2. **Monitoring**: Set up continuous quality monitoring
3. **Domain Adaptation**: Create domain-specific metrics
4. **Advanced MLflow**: Use MLflow for model registry and deployment

## Additional Resources

- **RAGas Documentation**: `@src/ragas_evaluation/basics/README.md`
- **MLflow Integration**: `@src/ragas_evaluation/with_mlflows/README.md`
- **Shared Utilities**: `@src/ragas_evaluation/shared/`
- **Project README**: `@README.md`
