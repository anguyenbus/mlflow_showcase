# RAGas Evaluation Basics

This directory contains fundamental examples demonstrating RAGas (RAG Assessment) package capabilities for evaluating Retrieval-Augmented Generation (RAG) systems using Zhipu AI backend integration.

## Overview

RAGas is a framework that helps you evaluate your RAG pipelines using a variety of metrics that measure:
- **Faithfulness**: Factual consistency of generated answers with retrieved context
- **Answer Relevancy**: How well the answer addresses the question
- **Context Precision**: Quality and relevance of retrieved contexts
- **Context Recall**: Completeness of retrieved contexts (requires ground truth)
- **Answer Correctness**: Accuracy compared to ground truth (requires ground truth)

## Prerequisites

Before running these examples, ensure you have:

1. **Set up your API key** in `.env` file:
   ```bash
   ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

2. **Install dependencies** (if needed):
   ```bash
   uv sync --all-extras --dev
   ```

3. **Prepare evaluation dataset** at `data/ragas_evaluation/evaluation_dataset.json`:
   ```json
   [
     {
       "question": "Your question here",
       "contexts": ["Context passage 1", "Context passage 2"],
       "response": "Generated response to evaluate",
       "reference_answer": "Ground truth answer (optional)"
     }
   ]
   ```

---

## Examples

### 1. Simple Evaluation (`simple_evaluation.py`)

**Overview:** Demonstrates the complete RAGas evaluation workflow from loading configuration to displaying results.

**What it demonstrates:**
- Loading RAGas configuration
- Loading evaluation dataset
- Configuring Zhipu AI backend with low temperature for consistent evaluation
- Creating RAGas evaluation with standard metrics
- Running evaluation on dataset
- Displaying results with rich console formatting

**Run the example:**
```bash
uv run python src/ragas_evaluation/basics/simple_evaluation.py
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

Step 5: Running RAGas evaluation...
✓ Evaluation complete!

Evaluation Results:
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Metric                ┃ Score    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ faithfulness          │   0.8500 │
│ answer_relevancy      │   0.9200 │
│ context_precision     │   0.7800 │
│ context_recall        │   0.8300 │
│ answer_correctness    │   0.7900 │
└───────────────────────┴──────────┘

Metric Interpretations:
[cyan]Faithfulness:[/cyan] Measures the factual consistency of the generated answer
against the retrieved context.

[yellow]Interpretation:[/yellow]
- Score 0.0-1.0, higher is better
- High score: Answer is factually consistent with context
- Low score: Answer contains hallucinations or contradicts context

... (additional metric interpretations)

Evaluation Summary
• Dataset size: 6 examples
• Metrics evaluated: 5
• Average score: 0.8340
• Backend: Zhipu AI (glm-5)
```

**Real-World Use Cases:**
- **Quality Assurance**: Regular evaluation of RAG system outputs
- **A/B testing**: Comparing different retrieval strategies or prompt templates
- **Performance monitoring**: Tracking RAG system quality over time
- **Debugging**: Identifying specific weaknesses in retrieval or generation
- **Benchmarking**: Establishing baseline metrics for system improvements

**Key concepts learned:**
- **RAGas metrics**: Understanding what each metric measures
- **Backend configuration**: Setting up LLM for evaluation (low temperature)
- **Evaluation workflow**: End-to-end evaluation process
- **Result interpretation**: Understanding and acting on metric scores

---

### 2. Metric Demonstration (`metric_demonstration.py`)

**Overview:** Provides individual demonstrations of each RAGas metric with detailed explanations and example scenarios.

**What it demonstrates:**
- Individual metric explanations
- Score interpretation guidelines
- Example scenarios for each metric
- Practical understanding of what metrics measure

**Run the example:**
```bash
uv run python src/ragas_evaluation/basics/metric_demonstration.py
```

**Expected output:**
```
RAGas Metrics Demonstration

╭─────────────────────────────────────────────────────────────────╮
│ Demonstrating Faithfulness Metric                              │
│ Measures factual consistency of answer against retrieved context│
╰─────────────────────────────────────────────────────────────────╯

[cyan]Faithfulness:[/cyan] Measures the factual consistency of the generated answer
against the retrieved context.

[yellow]Interpretation:[/yellow]
- Score 0.0-1.0, higher is better
- High score: Answer is factually consistent with context
- Low score: Answer contains hallucinations or contradicts context

[yellow]Example Scenario:[/yellow]
Question: What is the GST rate in Australia?
Context: 'GST is a broad-based tax of 10% on most goods, services and other items in Australia.'
Response (High Faithfulness): 'The GST rate in Australia is 10%.'
Response (Low Faithfulness): 'The GST rate in Australia is 15%.'

================================================================================

... (additional metric demonstrations)

╭─────────────────────────────────────────────────────────────────╮
│ All Metrics Demonstrated                                        │
╰─────────────────────────────────────────────────────────────────╮
• Faithfulness: Factual consistency with context
• Answer Relevancy: How well answer addresses question
• Context Precision: Quality of retrieved contexts
• Context Recall: Completeness of retrieved contexts (requires ground truth)
• Answer Correctness: Accuracy compared to ground truth (requires ground truth)
```

**Real-World Use Cases:**
- **Training material**: Educating team members on RAGas metrics
- **Onboarding**: Helping new developers understand evaluation concepts
- **Documentation reference**: Quick lookup for metric meanings
- **Stakeholder communication**: Explaining evaluation metrics to non-technical audiences

**Key concepts learned:**
- **Metric purposes**: Understanding what each metric evaluates
- **Score interpretation**: Knowing what good vs bad scores mean
- **Practical examples**: Seeing metrics in realistic scenarios
- **Ground truth requirements**: Understanding which metrics need reference answers

---

## Metric Interpretation Guide

### Faithfulness (Factual Consistency)

**What it measures:** Whether the generated answer is factually consistent with the retrieved context.

**Score range:** 0.0-1.0, higher is better

**Interpretation:**
- **High score (0.8-1.0)**: Answer is well-grounded in context, minimal hallucinations
- **Medium score (0.5-0.8)**: Some factual inconsistencies or minor hallucinations
- **Low score (0.0-0.5)**: Significant hallucinations or contradictions with context

**Common issues:**
- Low scores may indicate LLM is adding information not in context
- May need better context retrieval or prompt engineering
- Consider reducing temperature for generation

**Improvement strategies:**
- Improve retrieval quality to get more relevant context
- Add explicit instructions to use only provided context
- Use faithfulness as a signal for fine-tuning prompts

---

### Answer Relevancy (Question Addressing)

**What it measures:** How well the answer addresses the original question.

**Score range:** 0.0-1.0, higher is better

**Interpretation:**
- **High score (0.8-1.0)**: Answer directly and completely addresses the question
- **Medium score (0.5-0.8)**: Answer partially addresses question or is incomplete
- **Low score (0.0-0.5)**: Answer is irrelevant or misses the question's intent

**Common issues:**
- Low scores may indicate poor understanding of user intent
- May need better prompt engineering or context
- Could be due to incomplete retrieval

**Improvement strategies:**
- Improve question understanding in prompts
- Ensure retrieval covers all aspects of the question
- Add instructions to be comprehensive and direct

---

### Context Precision (Retrieval Quality)

**What it measures:** Quality and relevance of retrieved context passages.

**Score range:** 0.0-1.0, higher is better

**Interpretation:**
- **High score (0.8-1.0)**: Retrieved contexts are highly relevant and well-ranked
- **Medium score (0.5-0.8)**: Some irrelevant context in results
- **Low score (0.0-0.5)**: Many irrelevant contexts or poor ranking

**Common issues:**
- Low scores indicate poor retrieval quality
- May need better embedding models or chunking strategies
- Could be due to irrelevant documents in knowledge base

**Improvement strategies:**
- Improve document chunking and preprocessing
- Use better embedding models (e.g., larger models)
- Implement hybrid search (dense + sparse)
- Add re-ranking of retrieved documents

---

### Context Recall (Completeness)

**What it measures:** Whether all relevant information was retrieved from the knowledge base.

**Score range:** 0.0-1.0, higher is better

**Interpretation:**
- **High score (0.8-1.0)**: All relevant context was retrieved
- **Medium score (0.5-0.8)**: Some relevant context was missed
- **Low score (0.0-0.5)**: Significant information missing from retrieval

**Common issues:**
- Low scores indicate retrieval system is missing important information
- May need to increase number of retrieved documents
- Could be due to poor indexing or chunking

**Improvement strategies:**
- Increase top-k retrieval count
- Improve document indexing and chunking
- Use query expansion techniques
- Implement multiple retrieval strategies

**Note:** Requires ground truth reference answers.

---

### Answer Correctness (Accuracy)

**What it measures:** Accuracy of the generated answer compared to ground truth.

**Score range:** 0.0-1.0, higher is better

**Interpretation:**
- **High score (0.8-1.0)**: Answer matches ground truth closely
- **Medium score (0.5-0.8)**: Answer partially correct with some errors
- **Low score (0.0-0.5)**: Answer differs significantly from ground truth

**Common issues:**
- Low scores may indicate poor generation or retrieval
- Could be due to ambiguous ground truth
- May need better prompts or context

**Improvement strategies:**
- Improve retrieval quality and completeness
- Refine generation prompts
- Use few-shot examples in prompts
- Consider fine-tuning the model

**Note:** Requires ground truth reference answers.

---

## Troubleshooting

### Issue: Missing API Key

**Error:**
```
ERROR: ZHIPU_API_KEY environment variable is not set
```

**Solution:**
1. Get your API key from https://open.bigmodel.cn/
2. Copy `.env.example` to `.env`
3. Add your API key: `ZHIPU_API_KEY=your_key_here`
4. Run: `source .env` or reload your IDE

---

### Issue: Dataset Not Found

**Error:**
```
ERROR: Evaluation dataset not found at: /path/to/evaluation_dataset.json
```

**Solution:**
1. Create the data directory: `mkdir -p data/ragas_evaluation`
2. Create `evaluation_dataset.json` with your test data
3. See documentation for dataset structure examples
4. Ensure JSON is valid and properly formatted

---

### Issue: Invalid Dataset Structure

**Error:**
```
ERROR: Invalid dataset structure: Entry 0 is missing required fields: question
```

**Solution:**
1. Check that each entry has required fields: `question`, `contexts`, `response`
2. Ensure `contexts` is a list (even if single item)
3. Validate JSON format
4. See dataset structure examples in documentation

---

### Issue: Rate Limiting

**Error:**
```
ERROR: Rate limit exceeded for API calls
```

**Solution:**
1. Reduce dataset size for testing
2. Add delays between API calls
3. Use smaller models for faster evaluation
4. Consider batching evaluations

---

### Issue: Low Metric Scores

**Observation:** All metrics show very low scores (< 0.5)

**Possible causes:**
1. Poor quality retrieved context
2. Inadequate prompt engineering
3. Temperature too high for generation
4. Mismatch between questions and context

**Improvement strategies:**
1. Review and improve retrieval quality
2. Refine prompts for better generation
3. Use lower temperature (0.1-0.3) for evaluation
4. Ensure questions match available context

---

## Real-World Use Cases

### 1. Production Quality Monitoring

**Scenario:** Running a RAG system in production for customer support.

**Implementation:**
- Run `simple_evaluation.py` daily on sample of production queries
- Track metric trends over time in MLflow
- Set up alerts for significant metric drops
- Use results to identify degradation

**Benefits:**
- Early detection of quality issues
- Data-driven decisions for improvements
- Accountability for system changes

---

### 2. Retrieval Strategy Comparison

**Scenario:** Evaluating different retrieval approaches (dense vs hybrid search).

**Implementation:**
- Run evaluation with different retrieval configurations
- Compare metrics across approaches
- Use results to select best strategy
- Document trade-offs

**Benefits:**
- Data-driven retrieval optimization
- Understanding of performance trade-offs
- Evidence for architectural decisions

---

### 3. Prompt Engineering Iteration

**Scenario:** Improving generation prompts for better answers.

**Implementation:**
- Create evaluation dataset with representative queries
- Test different prompt variations
- Compare metrics across prompts
- Select best performing prompt

**Benefits:**
- Systematic prompt improvement
- Quantitative comparison of prompts
- Faster iteration cycles

---

### 4. Model Selection

**Scenario:** Choosing between different LLMs for generation.

**Implementation:**
- Run evaluation with different models
- Compare quality metrics and latency
- Consider cost-benefit trade-offs
- Make informed model selection

**Benefits:**
- Objective model comparison
- Understanding of quality-latency trade-offs
- Cost optimization

---

### 5. Regression Testing

**Scenario:** Ensuring system changes don't degrade quality.

**Implementation:**
- Establish baseline metrics with `simple_evaluation.py`
- Run evaluation after each significant change
- Compare new metrics to baseline
- Reject changes that significantly degrade metrics

**Benefits:**
- Prevent quality regression
- Confidence in deployments
- Systematic quality assurance

---

## Key Concepts Learned

### RAGas Evaluation Framework

1. **Metrics-Driven Evaluation**: Use quantitative metrics to assess RAG quality
2. **Multi-Dimensional Assessment**: Evaluate retrieval, generation, and correctness
3. **Ground Truth Flexibility**: Mix metrics with and without reference answers
4. **LLM-Based Evaluation**: Use LLMs as judges for automated assessment

### Backend Configuration

1. **Low Temperature for Evaluation**: Use 0.1-0.3 for consistent scoring
2. **Embedding Models**: Required for semantic similarity metrics
3. **API Integration**: Configure Zhipu AI with OpenAI-compatible endpoint
4. **Error Handling**: Validate environment and handle API failures

### Result Interpretation

1. **Score Ranges**: Understand 0.0-1.0 scale for all metrics
2. **Metric-Specific Insights**: Each metric measures different aspects
3. **Actionable Feedback**: Use scores to identify specific improvements
4. **Trend Analysis**: Track metrics over time for monitoring

### Production Considerations

1. **Quality Monitoring**: Regular evaluation for production systems
2. **Threshold Setting**: Define acceptable metric ranges
3. **Alerting**: Set up alerts for metric degradation
4. **Continuous Improvement**: Use evaluation for iterative optimization

---

## Next Steps

After completing these basic examples, explore:

1. **MLflow Integration**: See `with_mlflows/` for tracking experiments over time
2. **Advanced Metrics**: Explore custom metrics and evaluation strategies
3. **Production Pipelines**: Integrate evaluation into CI/CD
4. **Monitoring**: Set up continuous quality monitoring

---

## Additional Resources

- **RAGas Documentation**: https://docs.ragas.io/
- **Zhipu AI**: https://open.bigmodel.cn/
- **MLflow Documentation**: https://mlflow.org/docs/
- **Project README**: `/home/an/projects/tracing_project/README.md`
