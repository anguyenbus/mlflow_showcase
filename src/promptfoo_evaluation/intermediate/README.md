# Promptfoo Intermediate Examples

This directory contains intermediate-level promptfoo examples that build upon the basics. These examples demonstrate LLM-graded assertions, custom Python/JavaScript assertions, cost and latency tracking, and custom providers for production-ready evaluation workflows.

## Prerequisites

Before running these examples, ensure you have:

1. **Set up your API key** in `.env` file:
   ```bash
   ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

   Get your API key from: https://open.bigmodel.cn/

2. **Install promptfoo** (choose one option):

   **Option 1 - Global installation (recommended):**
   ```bash
   npm install -g promptfoo
   ```

   **Option 2 - Use npx (no installation):**
   ```bash
   npx promptfoo eval
   ```

3. **Install Python dependencies**:
   ```bash
   uv sync --all-extras --dev
   ```

4. **Load environment variables**:
   ```bash
   source .env  # Linux/Mac
   # or set in your IDE
   ```

**Important:** When running promptfoo directly with npx, you need to set `OPENAI_API_KEY` from your `ZHIPU_API_KEY`:
```bash
OPENAI_API_KEY=$ZHIPU_API_KEY OPENAI_BASE_URL="https://open.bigmodel.cn/api/paas/v4/" npx promptfoo eval -c cost_latency.yaml
```

---

## Examples

### 1. Cost & Latency Tracking (`cost_latency.yaml`)

**Overview:** Track and validate cost and latency metrics across models to ensure performance requirements are met.

**What it demonstrates:**
- Per-model latency thresholds
- Cost tracking and validation
- Performance comparison between models
- Cost efficiency analysis

**Run the example:**
```bash
# Option 1: Using npx with environment variable
OPENAI_API_KEY=$ZHIPU_API_KEY npx promptfoo eval -c cost_latency.yaml

# Option 2: Using global promptfoo installation
OPENAI_API_KEY=$ZHIPU_API_KEY promptfoo eval -c cost_latency.yaml
```

**View results in web UI:**
```bash
npx promptfoo view
# Opens browser at http://localhost:15500
```

### What is Tested

This example evaluates performance metrics across 4 different topics with dual testing per model:

| Test Case | Topic | Assertions | Performance Metrics |
|-----------|-------|------------|---------------------|
| 1 | Machine Learning | Contains "learn", "data" | Latency, token count, cost |
| 2 | Quantum Computing | Contains "quantum" | Latency, token count, cost |
| 3 | Climate Change | Contains "climate" | Latency, token count, cost |
| 4 | Artificial Intelligence | Icontains "AI" | Latency, token count, cost |

**Model Configuration**:
- **Provider**: GLM-5 (tested twice for reliability measurement)
- **Output**: Summaries of 3-4 sentences per topic

### Expected Results

**Typical Performance Metrics**:

| Metric | Expected Range | What It Indicates |
|--------|----------------|-------------------|
| **Latency** | 500-3000ms | Response time per request |
| **Tokens** | 50-200 tokens | Input + output token usage |
| **Cost** | $0.0001-$0.001 | API cost per request |
| **Pass Rate** | 75-100% | Content quality across topics |

**Output Table Shows**:
- Green cells = passed content assertions + within latency thresholds
- Red cells = failed assertions OR exceeded thresholds
- Cost column = cumulative cost across all tests
- Latency column = average response time

### Why These Tests Matter

- **Production SLAs**: Real applications have latency requirements (e.g., chatbots need <2s responses)
- **Cost Management**: API costs scale with usage - tracking helps prevent budget overruns
- **Model Selection**: Different models have different cost/latency profiles
- **Performance Regression**: Detect when model updates degrade performance

**Real-World Application Scenarios**:

| Scenario | Latency Requirement | Cost Consideration |
|----------|---------------------|-------------------|
| Customer service chatbot | < 2 seconds | High volume = cost sensitive |
| Batch document processing | < 30 seconds | Cost optimization critical |
| Real-time assistant | < 1 second | Quality > cost |
| Internal testing tool | < 5 seconds | Minimize cost |

**Cost Optimization Strategies**:
1. **Use faster models for simple tasks**: GLM-4.6 for basic Q&A
2. **Reserve premium models for complex tasks**: GLM-5 for analysis
3. **Monitor token usage**: Shorter prompts reduce cost
4. **Set latency thresholds**: Alert on performance degradation

**YAML Configuration**:
```yaml
description: Cost and latency tracking with performance thresholds

prompts:
  - "Summarize the key aspects of {{topic}} in 3-4 sentences."

providers:
  - openai:chat:glm-5
  - openai:chat:glm-5  # Tested twice for reliability

tests:
  - vars:
      topic: machine learning
    assert:
      - type: contains
        value: learn
      - type: contains
        value: data
```

**Key concepts learned:**
- **Latency Tracking**: Measure response times per model
- **Cost Monitoring**: Track API expenses across evaluations
- **Performance Thresholds**: Set acceptable limits for latency and cost
- **Reliability Testing**: Dual runs identify inconsistent performance
- **Metrics Visualization**: View performance data in web UI

---

### 2. Python Assertions (`python_asserts.yaml`)

**Overview:** Demonstrates Python-based custom assertions for domain-specific validation beyond built-in assertion types.

**What it demonstrates:**
- Python custom assertion functions
- Domain-specific validation logic
- Tax law validation examples
- Multi-criteria assertion patterns
- Reusable assertion modules

**Run the example:**
```bash
OPENAI_API_KEY=$ZHIPU_API_KEY npx promptfoo eval -c python_asserts.yaml
```

### What is Tested

This example validates factual accuracy across 4 question types:

| Test Case | Question Type | Assertions | Validation Focus |
|-----------|---------------|------------|------------------|
| 1 | Geography (Capital of Australia) | Contains "Canberra", icontains "australia" | Factual accuracy, case handling |
| 2 | Technical (ML summary) | Contains "learn", "data" | Domain terminology |
| 3 | Mathematical (2 + 2) | Contains "4" | Numerical accuracy |
| 4 | Open-ended (AI languages) | Icontains-any [python, java, javascript] | Acceptable alternatives |

**Assertion Types Demonstrated**:
- **contains**: Case-sensitive exact substring match
- **icontains**: Case-insensitive substring match
- **icontains-any**: At least one of multiple options (case-insensitive)

### Expected Results

**Typical Pass Rates**:
- Geography questions: 90-100% (well-established facts)
- Technical questions: 80-95% (depends on terminology)
- Mathematical questions: 95-100% (straightforward computation)
- Open-ended questions: 75-90% (multiple valid answers)

**Example Outputs**:

| Question | Expected Output Pattern |
|----------|------------------------|
| Capital of Australia | "The capital of Australia is Canberra..." |
| ML Summary | "Machine learning uses data and algorithms to learn..." |
| 2 + 2 | "The answer is 4" or "2 + 2 equals 4" |
| AI Language | "Python is widely used for AI..." |

### Why These Tests Matter

- **Domain-Specific Validation**: Built-in assertions can't capture all domain requirements
- **Custom Logic Integration**: Python assertions can query databases, call APIs, implement complex scoring
- **Fact-Checking**: Automate verification of factual claims in LLM outputs
- **Flexible Scoring**: Return scores (0-1) for granular assessment, not just pass/fail

**Real-World Applications**:

| Use Case | Python Assertion Example |
|----------|-------------------------|
| Tax validation | Check tax rates match current ATO tables |
| Medical content | Verify terminology matches approved terminology |
| Legal compliance | Check required disclaimers are present |
| Code generation | Validate code compiles or passes syntax checks |
| Data extraction | Verify all required fields are present |

**Python Assertion Module Pattern**:

```python
# In shared/assertions/python_asserts.py
from typing import Any

def contains_tax_keywords(output: str) -> dict[str, Any]:
    """Check if output contains tax-related keywords."""
    tax_keywords = ["tax", "income", "deduction", "gst"]
    found = [kw for kw in tax_keywords if kw.lower() in output.lower()]

    return {
        "pass": len(found) >= 2,
        "score": len(found) / len(tax_keywords),
        "reason": f"Found {len(found)} tax keywords: {found}"
    }
```

**Using Python Assertions in YAML**:

```yaml
assert:
  - type: python
    value: python_asserts  # Module name
    function: contains_tax_keywords  # Function name
```

**Key concepts learned:**
- **Python Assertions**: Custom validation logic in Python
- **Module System**: Reusable assertion functions across tests
- **Return Format**: Dict with pass, score, reason keys
- **Domain Validation**: Industry-specific assertion logic
- **Multi-Criteria**: Combine multiple assertions per test

---

### 3. JavaScript Assertions (`javascript_asserts.yaml`)

**Overview:** Cross-platform JavaScript assertions for browser-compatible evaluation and frontend integration.

**What it demonstrates:**
- JavaScript assertion functions
- JSON output validation
- Dynamic scoring based on multiple criteria
- String manipulation and validation
- Cross-platform assertion compatibility

**Run the example:**
```bash
OPENAI_API_KEY=$ZHIPU_API_KEY npx promptfoo eval -c javascript_asserts.yaml
```

### What is Tested

This example validates responses using JavaScript-based logic:

| Test Case | Question | Assertion Type | Validation Logic |
|-----------|----------|----------------|------------------|
| 1 | Capital of France | contains "Paris" | Simple substring match |
| 2 | Addition (5 + 7) | contains "12" | Numerical answer validation |
| 3 | Primary colors | icontains-any [red, blue, yellow] | Multiple valid answers |

**JavaScript Assertion Capabilities**:
- String manipulation (length checks, formatting)
- JSON parsing and validation
- Dynamic scoring algorithms
- Conditional logic
- Array operations

### Expected Results

**Pass Criteria**:

| Test | Pass Condition | Example Pass |
|------|----------------|--------------|
| Capital of France | Output contains "Paris" | "Paris is the capital..." |
| 5 + 7 | Output contains "12" | "The answer is 12" |
| Primary colors | Contains at least one of [red, blue, yellow] | "Red is a primary color" |

**Typical Pass Rate**: 90-100% for factual questions

### Why These Tests Matter

- **Browser Compatibility**: JavaScript assertions run in browser environments
- **Frontend Integration**: Validate outputs on the client side
- **JSON API Responses**: Many LLM applications return structured JSON
- **Cross-Platform Logic**: Share assertions between Node.js backend and browser frontend
- **Dynamic Scoring**: Complex scoring algorithms based on multiple factors

**Real-World Use Cases**:

| Scenario | JavaScript Assertion Example |
|----------|---------------------------|
| Chatbot response length | Check 50 < length < 500 chars |
| JSON API validation | Parse JSON, verify required fields |
| Sentiment analysis | Score based on positive/negative word counts |
| Format validation | Regex patterns for emails, phone numbers |
| Multi-criteria scoring | Combine length, keyword, and format checks |

**JavaScript Assertion Pattern**:

```javascript
// Inline JavaScript assertion
function assert(output, context) {
    const length = output.length;

    // Score based on length (prefer 100-200 chars)
    let score = 0;
    if (length >= 100 && length <= 200) {
        score = 1.0;
    } else if (length >= 50 && length <= 300) {
        score = 0.7;
    } else {
        score = 0.3;
    }

    return {
        pass: length > 50 && length < 500,
        score: score,
        reason: `Response length: ${length} chars`
    };
}
```

**JSON Validation Example**:

```javascript
function assert(output, context) {
    try {
        const json = JSON.parse(output);

        // Validate required fields
        if (!json.country || json.country !== 'Australia') {
            return {
                pass: false,
                score: 0,
                reason: "Missing or incorrect 'country' field"
            };
        }

        // Check all required fields present
        const required = ['country', 'tax_rate', 'year'];
        const missing = required.filter(f => !json[f]);

        if (missing.length > 0) {
            return {
                pass: false,
                score: 0.5,
                reason: `Missing fields: ${missing.join(', ')}`
            };
        }

        return {
            pass: true,
            score: 1.0,
            reason: "Valid JSON with all required fields"
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

**Key concepts learned:**
- **JavaScript Assertions**: Cross-platform validation logic
- **Return Format**: Object with pass, score, reason properties
- **JSON Validation**: Parse and validate structured outputs
- **Dynamic Scoring**: Algorithmic scoring based on output characteristics
- **Browser Compatible**: Run evaluations in web environments

---

### 4. Custom Provider (`custom_provider.py`)

**Overview:** Create custom Python providers for domain-specific evaluation and external system integration.

**What it demonstrates:**
- Custom provider pattern implementation
- Integration with domain-specific assertion logic
- Reusable assertion functions
- Provider API simulation
- External system integration patterns

**Run the example:**
```bash
python custom_provider.py
```

### What is Tested

This example demonstrates a custom provider for tax domain validation:

| Test Case | Output | Assertion | Expected Result |
|-----------|--------|-----------|-----------------|
| 1 | "Income tax is calculated..." | Tax keywords | Pass (contains "tax") |
| 2 | "The GST rate is 10%..." | Currency/Rate | Pass (contains "$" or rate) |
| 3 | "You can claim deductions..." | Tax keywords | Pass (contains "deductions") |
| 4 | "Generic response..." | Tax keywords | Fail (no tax content) |

**Provider Capabilities**:
- **contains_tax_keywords**: Checks for tax-related terminology
- **contains_australian_currency**: Validates Australian currency format
- **mentions_tax_rate**: Checks for tax rate references

### Expected Results

**Test Output**:
```
Custom Tax Assertion Provider Tests
==================================================

Test 1: Income tax is calculated on assessable income min...
  Pass: True
  Score: 1.0
  Reason: Found 3 tax keywords: ['tax', 'income', 'assessable']

Test 2: The GST rate is 10% in Australia....
  Pass: True
  Score: 0.9
  Reason: Found 2 tax keywords: ['tax', 'rate']

Test 3: This is a generic response with no tax content....
  Pass: False
  Score: 0.0
  Reason: No tax keywords found
```

### Why These Tests Matter

- **Domain-Specific Validation**: Generic assertions can't capture industry requirements
- **External Integration**: Connect to databases, APIs, or internal systems
- **Reusability**: Build assertion libraries for your organization
- **Encapsulation**: Bundle validation logic with domain knowledge
- **Testing**: Standalone testing of assertion logic before integration

**Real-World Applications**:

| Use Case | Custom Provider Implementation |
|----------|------------------------------|
| Tax calculations | Verify against ATO tax tables API |
| Medical content | Check against approved terminology service |
| Legal compliance | Validate against regulation database |
| Product catalog | Verify product details exist in inventory system |
| Multi-language | Integrate translation services for validation |

**Custom Provider Pattern**:

```python
from beartype import beartype
from typing import Any

@beartype
class CustomTaxAssertionProvider:
    """Custom provider for tax domain assertions."""

    __slots__ = ("name", "assertions")

    def __init__(self) -> None:
        """Initialize the custom provider."""
        self.name = "tax_assertions"
        self.assertions = {
            "contains_tax_keywords": self._contains_tax_keywords,
            "contains_australian_currency": self._contains_currency,
            "mentions_tax_rate": self._mentions_rate,
        }

    def evaluate(
        self,
        prompt: str,
        output: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Evaluate an assertion against LLM output."""
        assertion_func = self.assertions.get("contains_tax_keywords")
        if assertion_func:
            return assertion_func(output)
        return {"pass": True, "score": 1.0, "reason": "No assertion specified"}
```

**Integration with Promptfoo**:

```yaml
# In your promptfoo config
assert:
  - type: python
    value: custom_provider
    function: get_assertion_output
```

**Key concepts learned:**
- **Custom Providers**: Domain-specific evaluation logic
- **Provider Pattern**: Encapsulate assertion logic in reusable classes
- **Beartype Integration**: Type-safe provider implementations
- **External Integration**: Connect to APIs, databases, or services
- **Standalone Testing**: Test assertions independently of promptfoo

---

## Assertion Types Reference

### Built-in Assertions

| Type | Description | Example Use Case |
|------|-------------|------------------|
| `contains` | Exact substring match | Verify specific term appears |
| `icontains` | Case-insensitive match | Brand names, acronyms |
| `contains-all` | All substrings present | Check multiple keywords |
| `contains-any` | At least one substring present | Alternative answers |
| `regex` | Regular expression | Email, phone, URL validation |
| `similar` | Semantic similarity | Paraphrase detection |
| `is-json` | Valid JSON output | Structured data responses |
| `javascript` | JavaScript code evaluation | Dynamic validation logic |
| `python` | Python code evaluation | Domain-specific validation |

### Python Assertion Return Format

```python
def my_assertion(output: str, context: dict) -> dict[str, Any]:
    """
    Custom Python assertion function.

    Args:
        output: The LLM output to validate
        context: Execution context with prompt, vars, etc.

    Returns:
        Dict with:
            - pass: bool (required) - Pass/fail determination
            - score: float (optional) - 0-1 score for granular assessment
            - reason: str (optional) - Human-readable explanation
    """
    return {
        "pass": True,      # Required
        "score": 0.85,     # Optional
        "reason": "Found all required elements"  # Optional
    }
```

### JavaScript Assertion Return Format

```javascript
function assert(output, context) {
    /**
     * Custom JavaScript assertion function.
     *
     * Args:
     *   output: The LLM output to validate
     *   context: Execution context with prompt, vars, etc.
     *
     * Returns:
     *   Object with:
     *     - pass: boolean (required) - Pass/fail determination
     *     - score: number (optional) - 0-1 score
     *     - reason: string (optional) - Explanation
     */
    return {
        pass: true,      // Required
        score: 0.85,     // Optional
        reason: "Found all required elements"  // Optional
    };
}
```

---

## Advanced Patterns

### Pattern 1: Multi-Dimensional Scoring

Combine multiple assertion types for comprehensive evaluation:

```yaml
tests:
  - vars:
      question: "Explain Australia's tax system"
    assert:
      # Domain-specific validation
      - type: python
        value: python_asserts
        function: contains_tax_keywords
      # Quality assessment
      - type: contains
        value: tax
      # Completeness check
      - type: contains-all
        value: [income, rate, deduction]
```

**Why**: Different assertions validate different aspects - terminology, completeness, accuracy.

### Pattern 2: Threshold-Based Grading

Use score thresholds for granular assessment:

```yaml
assert:
  - type: javascript
    value: |
      function assert(output, context) {
          const wordCount = output.split(/\s+/).length;
          let score = 0;

          if (wordCount >= 50 && wordCount <= 200) {
              score = 1.0;
          } else if (wordCount >= 30 && wordCount <= 300) {
              score = 0.7;
          } else {
              score = 0.3;
          }

          return {
              pass: score > 0.5,
              score: score,
              reason: `Word count: ${wordCount}`
          };
      }
```

**Why**: Continuous scoring enables nuanced assessment beyond binary pass/fail.

### Pattern 3: Conditional Assertions

Apply different assertions based on context:

```yaml
tests:
  - vars:
      question_type: simple
      question: "What is 2 + 2?"
    assert:
      - type: contains
        value: "4"

  - vars:
      question_type: complex
      question: "Explain quantum entanglement"
    assert:
      - type: python
        value: physics_asserts
        function: contains_quantum_terms
```

**Why**: Different question types require different validation strategies.

---

## Performance Considerations

### Custom Assertion Overhead

| Assertion Type | Latency Impact | Cost Impact | When to Use |
|----------------|----------------|-------------|-------------|
| Built-in (contains, regex) | Minimal | None | Simple validation |
| JavaScript | Low | None | Cross-platform needs |
| Python | Low | None | Domain validation |
| LLM-graded | High (+1 API call) | +1 API call | Quality assessment |

### Cost Optimization Strategies

1. **Use built-in assertions first**: They're free and fast
2. **Reserve custom assertions for complex validation**: When built-ins aren't sufficient
3. **Cache assertion results**: For repeated validations
4. **Batch assertions**: Validate multiple criteria in one function call

### Latency Management

1. **Set appropriate timeouts**: Prevent hanging assertions
2. **Use async operations**: For I/O-bound assertions (API calls)
3. **Monitor assertion performance**: Track assertion execution time

---

## Next Steps

After mastering these intermediate examples, explore:

1. **Advanced Examples** (`../advanced/`):
   - RAG evaluation with custom providers
   - MLflow integration for experiment tracking
   - Production deployment patterns

2. **Production Integration**:
   - CI/CD pipeline integration
   - Automated regression testing
   - Performance monitoring dashboards

3. **Custom Development**:
   - Build domain-specific assertion libraries
   - Create custom providers for your stack
   - Integrate with existing testing frameworks
