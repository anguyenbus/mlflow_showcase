# Factuality Evaluation

## Overview

Factuality evaluation measures how accurately an LLM's responses align with known facts. Unlike general quality metrics, factuality focuses specifically on the correctness of factual claims - dates, numbers, names, relationships, and other verifiable information.

## Why It Matters

**Factual errors can have serious consequences**:

- **Medical applications**: Incorrect drug dosages or interactions
- **Financial services**: Wrong interest rates or regulations
- **Legal advice**: Inaccurate case law or statutes
- **Education**: Teaching incorrect information
- **Journalism**: Publishing false information

**Real-world example**: In 2023, Google's AI demo claimed that the James Webb Space Telescope took the first pictures of exoplanets. This was factually incorrect (it was actually the Very Large Telescope in 2004), causing embarrassment and raising concerns about AI reliability.

## Prerequisites

Before running this evaluation, ensure you have:

1. **ZHIPU_API_KEY environment variable**:
   ```bash
   export ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

2. **promptfoo installed**:
   ```bash
   npm install -g promptfoo
   ```

3. **Python dependencies**:
   ```bash
   uv sync --all-extras --dev
   ```

## Setup

### Configuration File

The `factuality.yaml` file defines:

- **Prompts**: Direct question format
- **Providers**: GLM-5 model via Zhipu AI
- **Default assertions**:
  - `factuality` (threshold: 0.7) - Measures factual accuracy
  - `contains` - Verifies expected answer is present

### Test Data

The `data/test_cases.json` file contains 12 test cases across 4 categories:

| Category | Examples | Verification Method |
|----------|----------|---------------------|
| **Dates** | Historical events, time periods | Contains/regex for year |
| **Numbers** | Scientific constants, quantities | Numerical extraction |
| **Entities** | Capital cities, people, places | Entity name verification |
| **Relationships** | Authorship, discoveries | Attribution verification |

## Running the Evaluation

### Option 1: Using the Python Runner (Recommended)

```bash
cd src/promptfoo_evaluation/advanced/evaluating_factuality
python factuality_test.py
```

### Option 2: Using promptfoo directly

```bash
cd src/promptfoo_evaluation/advanced/evaluating_factuality
OPENAI_API_KEY=$ZHIPU_API_KEY npx promptfoo eval -c factuality.yaml
```

### View Results

```bash
npx promptfoo view
# Opens browser at http://localhost:15500
```

## Understanding Results

### Metrics

| Metric | Description | Target Range |
|--------|-------------|--------------|
| **Overall Factuality Score** | Percentage of factually correct responses | >80% |
| **Extraction Accuracy** | How well facts are extracted from responses | >80% |
| **Verification Rate** | How many responses could be verified | >90% |

### Category Breakdown

Results show accuracy by information type:

| Category | What It Tests | Common Failure Modes |
|----------|---------------|---------------------|
| **Dates** | Historical accuracy | Off by one year, wrong century |
| **Numbers** | Numerical precision | Order of magnitude errors |
| **Entities** | Named entity recognition | Wrong person, place, or thing |
| **Relationships** | Attribution accuracy | Wrong creator, discoverer, etc. |

### Interpreting Scores

- **90-100%**: Excellent - Model is highly reliable for factual queries
- **80-90%**: Good - Minor errors occasionally
- **70-80%**: Fair - Regular factual mistakes
- **<70%**: Poor - Not suitable for factual applications

### Error Analysis

Common factual error types:

1. **Hallucinations**: Model invents plausible-sounding but false information
2. **Confusion**: Mixes up similar entities (e.g., Sydney vs Canberra)
3. **Approximation**: Rounds numbers inappropriately
4. **Attribution errors**: Credits wrong person/source

## Best Practices

### 1. Ground Truth Preparation

**High-quality ground truth is essential**:

```json
{
  "question": "What is the speed of light?",
  "expected_answer": "299,792,458",
  "tolerance": "exact",
  "unit": "m/s",
  "alternative": "3 x 10^8"
}
```

**Best practices**:
- Verify all ground truth against authoritative sources
- Include common alternative answers
- Specify units for numerical values
- Note any acceptable approximations

### 2. Assertion Selection

Use appropriate assertions for each fact type:

| Fact Type | Recommended Assertions |
|-----------|----------------------|
| **Exact values** | `contains`, `equals` |
| **Names** | `contains-all`, `icontains` |
| **Dates** | `contains`, regex patterns |
| **Numbers** | Python assertions with tolerance |
| **Lists** | `contains-all`, `contains-any` |
| **Relationships** | Python with logical checks |

**Example - Numerical with tolerance**:
```python
def assert_fn(output, context):
    """Check speed of light with acceptable precision."""
    # Accept: 299,792,458 or 3e8 or 3 x 10^8
    has_exact = "299792458" in output.replace(",", "")
    has_approx = "3e8" in output.lower() or "3 x 10" in output
    return {
        "pass": has_exact or has_approx,
        "score": 1.0 if has_exact else 0.9,
        "reason": "Speed of light accepted"
    }
```

### 3. Handling Partial Credit

Not all errors are equal. Use scoring for partial credit:

```python
def assert_fn(output, context):
    """Graded factuality check."""
    expected = "Canberra"
    output_lower = output.lower()

    # Full credit
    if expected.lower() in output_lower:
        return {"pass": True, "score": 1.0, "reason": "Correct"}

    # Partial credit - mentions Australia correctly
    if "australia" in output_lower:
        return {"pass": False, "score": 0.5, "reason": "Wrong city, right country"}

    # No credit
    return {"pass": False, "score": 0.0, "reason": "Incorrect"}
```

### 4. Domain-Specific Factuality

Different domains have different factuality requirements:

| Domain | Factuality Requirement | Strategy |
|--------|----------------------|----------|
| **Medical** | Near-perfect | Use RAG with verified sources |
| **Legal** | High with citations | Require source attribution |
| **News** | High with verification | Multiple source checking |
| **General knowledge** | High | Regular factuality testing |
| **Creative** | Lower | Allow creative license |

### 5. Reducing Hallucinations

**Strategies to improve factuality**:

1. **Temperature control**: Use lower temperatures (0.0-0.3)
2. **Knowledge cutoff awareness**: Note date limitations
3. **Uncertainty signaling**: Prompt model to say "I'm not sure"
4. **Source requirements**: Require citations for factual claims
5. **RAG integration**: Augment with reliable sources

**Example prompt**:
```
Answer the following question accurately.
If you're not certain of the answer, say so.
Do not make up facts or guess.

Question: {{question}}
```

### 6. Continuous Testing

**Factuality can degrade over time**:

- Model updates may change behavior
- Training data cutoffs become more distant
- New facts emerge that models don't know

**Testing schedule**:
- **Before model updates**: Baseline current performance
- **After model updates**: Compare to baseline
- **Monthly**: For critical applications
- **When new facts emerge**: Add test cases

### 7. Production Monitoring

**Track in production**:

| Metric | How to Track | Alert Threshold |
|--------|--------------|-----------------|
| User corrections | Feedback mechanism | >5% correction rate |
| Factual disputes | Support tickets | Spike indicates issues |
| Source conflicts | Multiple source checks | Inconsistencies |
| Confidence scores | Model confidence | Low confidence patterns |

## Further Reading

### Research on Factuality
- [Factual Accuracy in Language Models](https://arxiv.org/abs/2305.14351) - Survey of factuality
- [Measuring Factual Accuracy](https://arxiv.org/abs/2306.05684) - FAVA framework
- [FactScore: Factuality Evaluation](https://arxiv.org/abs/2305.14227) - Biographies

### Evaluation Frameworks
- [RAGAS Faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/faithfulness/) - RAG factuality
- [DeepEval Factuality](https://docs.deep-eval.org/en/latest/metrics-factuality.html) - Factuality metric
- [ TruLens](https://www.trulens.org/) - Context faithfulness

### Related Examples
- `../prevent_hallucination/` - Detecting when model lacks information
- `../rag_pipeline/` - Factuality with retrieved context
- `../../basics/assertions_guide.yaml` - Assertion patterns

## Real-World Use Cases

| Application | Factuality Risk | Mitigation |
|-------------|----------------|------------|
| **Medical diagnosis** | Patient harm | RAG with verified sources, low temperature |
| **Financial advice** | Regulatory violation | Compliance checks, human review |
| **News generation** | Misinformation | Source verification, fact-checking |
| **Education** | Learning incorrect info | Expert review, textbook alignment |
| **Legal research** | Malpractice | Case database verification |
| **Code documentation** | Security issues | Syntax validation, testing |
| **Product descriptions** | False advertising | Database validation |
| **Scientific writing** | Research errors | Citation verification, peer review |
