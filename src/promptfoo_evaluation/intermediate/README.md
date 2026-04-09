# Promptfoo Intermediate Examples

This directory contains advanced promptfoo examples demonstrating LLM-graded assertions, custom Python/JavaScript assertions, cost and latency tracking, and custom providers.

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

---

## Examples

### 1. Python Assertions (`python_asserts.yaml`)

**Overview:** Demonstrates LLM-graded assertions and Python custom assertions.

**What it demonstrates:**
- LLM-graded assertions (`llm-rubric`, `factuality`, `answer-relevance`)
- Python custom assertion functions
- Domain-specific assertions (tax law validation)
- Context-faithfulness checking for RAG applications
- Multi-dimensional scoring

**Run the example:**
```bash
npx promptfoo eval -c python_asserts.yaml
```

**LLM-Graded Assertions:**

LLM-graded assertions use another LLM call to evaluate the quality of the response:

```yaml
assert:
  - type: llm-rubric
    value: |
      The response correctly identifies Australian tax rates including:
      - 0% threshold ($18,200)
      - 19% rate bracket
      - At least one other rate bracket
      Score 1.0 if all present, 0.5 if partial, 0.0 if missing
```

**Python Custom Assertions:**

Use Python functions for domain-specific validation:

```yaml
assert:
  - type: python
    value: python_asserts
    function: mentions_tax_rate
```

The Python module (`shared/assertions/python_asserts.py`) provides:

```python
def mentions_tax_keywords(output: str) -> dict[str, Any]:
    """Check if output contains tax-related keywords."""
    tax_keywords = ["tax", "income", "deduction", "gst", ...]
    # Returns: {"pass": bool, "score": float, "reason": str}
```

**Real-World Use Cases:**
- **Domain Validation**: Check for industry-specific terminology
- **Quality Assurance**: Automated response quality evaluation
- **Fact-Checking**: Verify factual accuracy of responses
- **RAG Evaluation**: Measure context faithfulness and relevance

---

### 2. Cost & Latency Tracking (`cost_latency.yaml`)

**Overview:** Track and validate cost and latency metrics across models.

**What it demonstrates:**
- Per-model latency thresholds
- Cost tracking and validation
- Performance comparison between models
- Cost efficiency analysis

**Run the example:**
```bash
npx promptfoo eval -c cost_latency.yaml
```

**Setting Thresholds:**

```yaml
defaultTest:
  options:
    maxLatencyMs:
      openai:chat:glm-5-flash: 2000
      openai:chat:glm-5-plus: 5000
    maxCost:
      openai:chat:glm-5-flash: 0.001
      openai:chat:glm-5-plus: 0.005
```

**Custom Metrics:**

```javascript
// Cost efficiency check
function assert(output, context) {
    const cost = context?.cost || 0;
    const length = output?.length || 0;
    const costPerChar = cost / length;

    return {
        pass: costPerChar < 0.0001,
        score: Math.max(0, 1 - costPerChar * 10000),
        reason: `Cost per char: $${costPerChar.toFixed(6)}`
    };
}
```

**Real-World Use Cases:**
- **Performance SLAs**: Ensure responses meet latency requirements
- **Cost Optimization**: Choose the most cost-effective model
- **Capacity Planning**: Model selection based on expected load
- **Budget Management**: Track and control API costs

---

### 3. JavaScript Assertions (`javascript_asserts.yaml`)

**Overview:** Cross-platform JavaScript assertions for browser-compatible evaluation.

**What it demonstrates:**
- JavaScript assertion functions
- JSON output validation
- Dynamic scoring based on multiple criteria
- String manipulation and validation

**Run the example:**
```bash
npx promptfoo eval -c javascript_asserts.yaml
```

**JavaScript Assertion Pattern:**

```yaml
assert:
  - type: javascript
    value: |
      function assert(output, context) {
          // Your validation logic
          const length = output.length;

          return {
              pass: length > 50 && length < 500,
              score: Math.min(1, length / 100),
              reason: `Response length: ${length} chars`
          };
      }
```

**Example: JSON Validation**

```javascript
function assert(output, context) {
    try {
        const json = JSON.parse(output);

        if (!json.country || json.country !== 'Australia') {
            return {
                pass: false,
                score: 0,
                reason: "Missing or incorrect 'country' field"
            };
        }

        return {
            pass: true,
            score: 1.0,
            reason: "Valid JSON with correct country"
        };
    } catch (e) {
        return {
            pass: false,
            score: 0,
            reason: `Invalid JSON: ${e.message}`
        };
    }
}
```

**Real-World Use Cases:**
- **Browser-Based Testing**: Run evaluations in web environments
- **JSON API Responses**: Validate structured outputs
- **Frontend Integration**: Client-side assertion validation
- **Cross-Platform Logic**: Share assertions between Node.js and browser

---

### 4. Custom Provider (`custom_provider.py`)

**Overview:** Create custom Python providers for domain-specific evaluation.

**What it demonstrates:**
- Custom provider pattern implementation
- Integration with domain-specific assertion logic
- Reusable assertion functions
- Provider API simulation

**Run the example:**
```bash
python custom_provider.py
```

**Custom Provider Structure:**

```python
from beartype import beartype

@beartype
class CustomTaxAssertionProvider:
    """Custom provider for tax domain assertions."""

    def __init__(self) -> None:
        self.name = "tax_assertions"
        self.assertions = {
            "contains_tax_keywords": contains_tax_keywords,
            "contains_australian_currency": contains_australian_currency,
            "mentions_tax_rate": mentions_tax_rate,
        }

    def evaluate(self, prompt: str, output: str, context: dict) -> dict:
        """Evaluate an assertion against LLM output."""
        assertion_func = self.assertions.get("contains_tax_keywords")
        return assertion_func(output)
```

**Using with Promptfoo:**

```yaml
# In your promptfoo config
assert:
  - type: python
    value: custom_provider
    function: get_assertion_output
```

**Real-World Use Cases:**
- **Domain-Specific Validation**: Industry-specific assertion logic
- **External API Integration**: Validate against external systems
- **Custom Scoring**: Complex scoring algorithms
- **Legacy System Integration**: Connect with existing validation systems

---

## Assertion Types Reference

### LLM-Graded Assertions

| Type | Description | Use Case |
|------|-------------|----------|
| `llm-rubric` | Custom rubric-based grading | Qualitative assessment |
| `factuality` | Factual accuracy check | Hallucination detection |
| `answer-relevance` | Answer relevance scoring | Response quality |
| `context-recall` | Context usage measurement | RAG evaluation |
| `context-faithfulness` | Context adherence check | Grounding verification |

### Python Assertions

Return format:

```python
def my_assertion(output: str, context: dict) -> dict[str, Any]:
    return {
        "pass": bool,      # Required: pass/fail
        "score": float,    # Optional: 0-1 score
        "reason": str,     # Optional: explanation
    }
```

### JavaScript Assertions

Return format:

```javascript
function assert(output, context) {
    return {
        pass: true/false,  // Required
        score: 0.0-1.0,    // Optional
        reason: "..."      // Optional
    };
}
```

---

## Advanced Patterns

### Pattern 1: Multi-Dimensional Scoring

Combine multiple assertion types for comprehensive evaluation:

```yaml
assert:
  - type: python
    value: python_asserts
    function: contains_tax_keywords
  - type: llm-rubric
    value: "Response is accurate and complete"
  - type: answer-relevance
    threshold: 0.7
```

### Pattern 2: Conditional Assertions

Apply different assertions based on context:

```yaml
tests:
  - vars:
      question_type: simple
    assert:
      - type: javascript
        value: "simple_assert"
  - vars:
      question_type: complex
    assert:
      - type: javascript
        value: "complex_assert"
```

### Pattern 3: Threshold-Based Grading

Use thresholds for granular assessment:

```yaml
assert:
  - type: answer-relevance
    threshold: 0.9  # High bar
  - type: context-faithfulness
    threshold: 0.7  # Medium bar
  - type: factuality
    threshold: 0.5  # Lower bar
```

---

## Performance Considerations

### LLM-Graded Assertion Overhead

LLM-graded assertions make additional API calls:

| Factor | Impact | Mitigation |
|--------|--------|------------|
| API calls | 2x latency | Cache results |
| Cost | 2x cost | Use for testing only |
| Quality | Higher accuracy | Balance with simple assertions |

### Cost Optimization

1. **Use fast models for assertions**: `glm-5-flash` for grading
2. **Batch assertions**: Evaluate multiple criteria in one call
3. **Selective grading**: Only use LLM-grading for critical tests

### Latency Management

1. **Set appropriate timeouts**: Prevent hanging evaluations
2. **Use async evaluation**: Parallel test execution
3. **Monitor thresholds**: Catch performance regressions

---

## Next Steps

After mastering these intermediate examples, explore:

1. **Advanced Examples**:
   - RAG evaluation with custom providers
   - MLflow integration for experiment tracking
   - Production deployment patterns

2. **Production Integration**:
   - CI/CD pipeline integration
   - Automated regression testing
   - Performance monitoring

3. **Custom Development**:
   - Build domain-specific assertion libraries
   - Create custom providers for your stack
   - Integrate with existing testing frameworks
