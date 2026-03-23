# Evaluation Framework: Metrics and Assessment

This guide covers MLflow's evaluation framework for LLM applications. You'll learn about standard metrics, custom evaluation, and result interpretation.

## Prerequisites

- Completed [01-basics-tracking.md](01-basics-tracking.md)
- MLflow UI running at http://localhost:5000
- Zhipu AI API key configured

## What is LLM Evaluation?

Evaluation measures how well your LLM application performs on specific tasks:

- **Summarization**: ROUGE metrics (overlap with reference summaries)
- **Question Answering**: Exact match, relevance scores
- **Custom Metrics**: Domain-specific evaluation criteria
- **LLM-as-a-Judge**: Using LLMs to evaluate responses

## Exercise 1: ROUGE Metrics for Summarization

Evaluate text summarization using ROUGE (Recall-Oriented Understudy for Gisting Evaluation).

1. **Run the ROUGE evaluation example:**

```bash
uv run python src/intermediate/evaluate_summarization.py
```

2. **Expected output:**

```
Creating summarization dataset...
Running ROUGE evaluation...
ROUGE-1: 0.75
ROUGE-2: 0.62
ROUGE-L: 0.71
Evaluation complete
View results at: http://localhost:5000/experiments/...
```

3. **View results in MLflow UI:**

- Navigate to the evaluation run
- Check the "Metrics" section for ROUGE scores
- Review the evaluation table artifact

### Understanding ROUGE Metrics

**ROUGE-1**: Overlap of unigrams (single words)

```
Reference: "The cat sat on the mat."
Candidate: "The dog sat on the rug."
Overlap: "The", "sat", "on", "the" = 4/6
```

**ROUGE-2**: Overlap of bigrams (word pairs)

```
Reference: ["The cat", "cat sat", "sat on"]
Candidate: ["The dog", "dog sat", "sat on"]
Overlap: "sat on" = 1/3
```

**ROUGE-L**: Longest common subsequence

```
Measures the longest sequence of words that appear in both texts
in the same order, regardless of position.
```

**Interpreting scores:**

- 0.0-0.2: Poor overlap
- 0.2-0.4: Fair overlap
- 0.4-0.6: Good overlap
- 0.6-0.8: Very good overlap
- 0.8-1.0: Excellent overlap

## Exercise 2: Exact Match Evaluation

Evaluate question-answering with exact match metrics.

1. **Run the QA evaluation example:**

```bash
uv run python src/intermediate/evaluate_qa.py
```

2. **Expected output:**

```
Loading QA dataset...
Running exact match evaluation...
Exact Match Rate: 0.80 (8/10)
Evaluation complete
```

3. **View results in MLflow UI:**

- Check the evaluation table for detailed results
- Look for examples that passed/failed exact match
- Review error analysis for failed cases

### Understanding Exact Match

**What it measures:**

```python
# Exact match: response must match ground truth exactly
ground_truth = "The tax rate is 32.5%."
response = "The tax rate is 32.5%."  # Match: True

response = "The tax rate is 32.5 percent."  # Match: False
```

**When to use it:**

- Fact-based questions with single correct answers
- Calculations with specific numeric answers
- Terminology and definition questions
- Structured data extraction

**Limitations:**

- Very strict: minor differences cause failures
- Doesn't capture semantic similarity
- Not suitable for open-ended questions

## Exercise 3: Custom Metrics

Create domain-specific evaluation metrics.

1. **Run the custom metrics example:**

```bash
uv run python src/intermediate/evaluate_custom_metrics.py
```

2. **Expected output:**

```
Creating custom metric: legal_citation_accuracy
Evaluating with custom metric...
Legal Citation Accuracy: 0.70
Custom evaluation complete
```

3. **View the custom metric:**

- In MLflow UI, check for the custom metric name
- Review the evaluation logic in the source code

### Creating Custom Metrics

**Using mlflow.metrics.make_metric():**

```python
import mlflow

def citation_accuracy_evaluator(predictions, targets):
    """Calculate citation accuracy."""
    correct = 0
    for pred, target in zip(predictions, targets):
        # Check if response contains legal citations
        if "§" in pred and "Income Tax Act" in pred:
            correct += 1
    return correct / len(predictions)

# Create custom metric
citation_metric = mlflow.metrics.make_metric(
    eval_fn=citation_accuracy_evaluator,
    greater_is_better=True,
    name="legal_citation_accuracy"
)

# Use in evaluation
results = mlflow.evaluate(
    model=model,
    data=eval_data,
    metrics=[citation_metric]
)
```

**Best practices for custom metrics:**

- Use descriptive names
- Document what the metric measures
- Specify if higher or lower is better
- Test on known examples first

## Exercise 4: LLM-as-a-Judge

Use LLMs to evaluate response quality.

1. **Run the LLM judge example:**

```bash
uv run python src/advanced/evaluate_llm_judge.py
```

2. **Expected output:**

```
Creating LLM judge...
Evaluating responses with LLM judge...
Response Quality: 0.85
Relevance: 0.90
Completeness: 0.80
LLM judge evaluation complete
```

3. **View LLM judge results:**

- Check the qualitative assessment scores
- Review the judge prompt template
- Analyze judge feedback

### Understanding LLM-as-a-Judge

**What it is:**

```python
# Use an LLM to evaluate another LLM's responses
judge_prompt = """
Rate the following response on a scale of 1-10:
Question: {question}
Response: {response}

Consider:
- Accuracy
- Relevance
- Completeness
- Clarity

Score:
"""
```

**Advantages:**

- Captures nuanced quality aspects
- Evaluates open-ended responses
- Provides qualitative feedback
- Can assess reasoning and logic

**Challenges:**

- More expensive (requires LLM calls)
- May be inconsistent
- Requires good prompt engineering
- Potential for bias

## Exercise 5: Baseline Comparison

Compare different model variants or configurations.

1. **Run the baseline comparison example:**

```bash
uv run python src/advanced/evaluate_baselines.py
```

2. **Expected output:**

```
Evaluating baseline model...
Baseline ROUGE-1: 0.65
Evaluating improved model...
Improved ROUGE-1: 0.72
Improvement: +0.07
Comparison complete
```

3. **View comparison in MLflow UI:**

- Compare runs side by side
- Check metric improvements
- View charts showing progress over time

### Interpreting Evaluation Results

**Metric comparison:**

```python
# Compare metrics across runs
baseline_rouge = 0.65
improved_rouge = 0.72
improvement = ((improved_rouge - baseline_rouge) / baseline_rouge) * 100
# improvement = 10.8%
```

**Statistical significance:**

- Small improvements (1-2%) may not be significant
- Use multiple test examples for reliability
- Consider confidence intervals for important metrics

**Business impact:**

- Translate metric improvements to user impact
- Consider cost-benefit tradeoffs
- Monitor metrics in production

## Evaluation Datasets

### Creating Quality Datasets

**Dataset characteristics:**

- **Representative**: Covers real use cases
- **Balanced**: Includes different question types
- **Sized appropriately**: 10-100 examples for initial eval
- **Ground truth**: Accurate reference answers

**Example: Australian Tax Law Dataset**

```python
# @data/evaluation/tax_law_qa.csv
question,answer,category
"What is the tax rate for income between $45,001 and $120,000?","The tax rate is 32.5% for income between $45,001 and $120,000 for Australian residents.",tax_rates
"What are allowable deductions?","Allowable deductions include work-related expenses, business operating expenses, investment expenses, and charitable donations.",deductions
```

### Loading Evaluation Data

```python
import pandas as pd

# Load evaluation dataset
eval_df = pd.read_csv("data/evaluation/tax_law_qa.csv")

# Prepare for MLflow evaluation
eval_data = eval_df[["question"]].rename(columns={"question": "inputs"})
eval_data["ground_truth"] = eval_df["answer"]
```

## Best Practices

### Metric Selection

- **Summarization**: Use ROUGE metrics
- **QA**: Use exact match + relevance
- **Open-ended**: Use LLM-as-a-judge
- **Domain-specific**: Create custom metrics

### Evaluation Workflow

1. **Define success criteria** before evaluation
2. **Create balanced dataset** representing real use cases
3. **Run evaluation** on multiple model variants
4. **Analyze results** in MLflow UI
5. **Iterate** based on findings

### Common Pitfalls

- **Data leakage**: Don't use training data for evaluation
- **Small datasets**: Use at least 10-20 examples
- **Single metric**: Evaluate multiple dimensions
- **Ignoring errors**: Analyze failed cases

## Verification Checklist

Before moving to the next guide, verify:

- [ ] ROUGE metrics calculate correctly
- [ ] Exact match evaluation works
- [ ] Custom metrics evaluate domain-specific criteria
- [ ] LLM judge provides qualitative assessment
- [ ] Baseline comparisons show improvements
- [ ] Evaluation results visible in MLflow UI

## Troubleshooting

**Issue: ROUGE scores are very low**

- Solution: Check if reference summaries are appropriate for your use case

**Issue: Exact match always fails**

- Solution: Consider fuzzy matching or semantic similarity for your use case

**Issue: Custom metric errors**

- Solution: Verify your evaluation function returns a float value

**Issue: LLM judge is slow**

- Solution: Use a faster model for judging (e.g., glm-5-flash)

## Next Steps

- **[04-rag-implementation.md](04-rag-implementation.md)** - Build RAG systems with evaluation

## Additional Resources

- [MLflow Evaluation Documentation](https://mlflow.org/docs/latest/evaluation.html)
- Evaluation examples: @src/intermediate/evaluate_*.py
