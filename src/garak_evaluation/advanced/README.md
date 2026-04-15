# Garak Advanced Evaluation Tutorials

This directory contains advanced-level tutorials for using Garak (Generative AI Red-teaming & Assessment Kit) to systematically assess LLM security vulnerabilities. These tutorials are aligned with OWASP LLM Top 10 threat categories and mapped to the CPH Sec AI Red Team Lifecycle phases.

## Prerequisites

Before running these evaluations, ensure you have:

1. **Set up your API key** in `.env` file:
   ```bash
   ZHIPU_API_KEY=your_zhipu_api_key_here
   ```

   Get your API key from: https://open.bigmodel.cn/

2. **Install Garak**:
   ```bash
   uv pip install garak
   ```

3. **Install Python dependencies**:
   ```bash
   uv sync --all-extras --dev
   ```

---

## Quick Start

### Run All Evaluations

```bash
# Navigate to the advanced directory
cd src/garak_evaluation/advanced

# Run all evaluations using the unified analysis script
python analyze_all.py

# Or run individual topics (see below)
```

### Run Individual Topic Evaluations

Each topic can be evaluated using three approaches:

1. **CLI-based execution**:
   ```bash
   garak --model_type openai-compatible --model_name glm-4-plus \
         --probe_type dan.DAN --openai_base https://open.bigmodel.cn/api/paas/v4/
   ```

2. **YAML configuration**:
   ```bash
   garak -c topic_name/topic_name_cli.yaml
   ```

3. **Python API**:
   ```bash
   cd topic_name
   python topic_name_test.py
   ```

---

## Topics

### 1. Prompt Injection (`prompt_injection/`)

**Overview:** Testing for direct and indirect prompt injection attacks that attempt to manipulate model behavior through encoded payloads.

**OWASP Category:** LLM01 - Prompt Injection

**What it tests:**
- Base64 and ROT13 encoding injection
- Web-based injection patterns
- Latent injection in structured data (JSON, XML)
- Unicode confusable attacks

**Run the example:**
```bash
cd prompt_injection
python prompt_injection_test.py
```

**Key Features:**
- 8 test scenarios covering encoding variations
- Encoding-based probe detection
- Web injection pattern detection
- Latent injection in structured formats

**[Full Documentation & Guide](prompt_injection/README.md)**

---

### 2. Jailbreaks (`jailbreaks/`)

**Overview:** Evaluating model resistance to jailbreak attempts that bypass safety guardrails.

**OWASP Category:** LLM01 - Prompt Injection (Jailbreaks)

**What it tests:**
- DAN (Do Anything Now) variants
- Grandma exploit patterns
- Goodside attack patterns
- Role-playing jailbreaks

**Run the example:**
```bash
cd jailbreaks
python jailbreaks_test.py
```

**Key Features:**
- 8 jailbreak pattern test cases
- Refusal rate tracking
- Persona adoption detection
- Boundary violation testing

**[Full Documentation & Guide](jailbreaks/README.md)**

---

### 3. Data Leakage (`data_leakage/`)

**Overview:** Detecting training data replay and sensitive information leakage.

**OWASP Category:** LLM06 - Training Data Poisoning & Leakage

**What it tests:**
- Training data extraction attempts
- PII (Personally Identifiable Information) leakage
- Credential and secret leakage
- Memorized content detection

**Run the example:**
```bash
cd data_leakage
python data_leakage_test.py
```

**Key Features:**
- 8 data extraction test scenarios
- Sensitive data pattern detection
- Training data replay detection
- Leakage rate calculation

**[Full Documentation & Guide](data_leakage/README.md)**

---

### 4. Malicious Content (`malicious_content/`)

**Overview:** Testing for malicious code generation and harmful content production.

**OWASP Category:** LLM03 - Data Poisoning & Model Theft

**What it tests:**
- Malware generation attempts
- Package hallucination (fake PyPI/npm packages)
- Dangerous instruction requests
- Harmful content production

**Run the example:**
```bash
cd malicious_content
python malicious_content_test.py
```

**Key Features:**
- 8 malicious content test scenarios
- Malicious code pattern detection
- Package name validation
- Harmful content detection

**[Full Documentation & Guide](malicious_content/README.md)**

---

## Comparison Table

| Topic | Probe Categories | OWASP Category | Test Count | Key Metrics | CPH Sec Phase |
|-------|-----------------|----------------|------------|-------------|---------------|
| **Prompt Injection** | encoding, web_injection, latentinjection | LLM01 | 8 | Pass rate, injection success | Attack Vector ID |
| **Jailbreaks** | DAN, Grandma, Goodside | LLM01 | 8 | Refusal rate, boundary violations | Attack Vector ID |
| **Data Leakage** | replay, PII, credentials | LLM06 | 8 | Leakage rate, sensitive data found | Execution & Analysis |
| **Malicious Content** | malware, packages, dangerous | LLM03 | 8 | Refusal rate, harmful content | Execution & Analysis |

---

## CPH Sec AI Red Team Lifecycle

These tutorials map to the CPH Sec AI Red Team Lifecycle:

### Phase 1: Planning and Reconnaissance

- **Activities in tutorials:**
  - Identify LLM applications to test (Zhipu GLM models)
  - Map model capabilities and interfaces
  - Review documentation and API specs
  - Define testing boundaries

### Phase 2: Threat Modeling and Prioritization

- **Activities in tutorials:**
  - Map to OWASP LLM Top 10 categories
  - Identify high-risk probe categories (injection, jailbreaks, leakage, malicious content)
  - Prioritize testing based on potential impact
  - Document threat assumptions for each probe type

### Phase 3: Attack Vector Identification

- **Activities in tutorials:**
  - Select appropriate Garak probes for each threat category
  - Configure test parameters (model, probes, detectors)
  - Prepare test data and payloads (test_cases.txt files)
  - Set up monitoring and logging (JSONL output)

### Phase 4: Execution and Analysis

- **Activities in tutorials:**
  - Execute Garak probes via CLI, YAML, or Python API
  - Monitor evaluation progress
  - Parse and analyze JSONL results
  - Identify successful attacks and vulnerabilities

### Phase 5: Reporting and Remediation

- **Activities in tutorials:**
  - Generate vulnerability reports with severity classification
  - Provide remediation recommendations
  - Document findings in structured format
  - Track remediation progress

---

## Progressive Learning Path

```
Prerequisites
    ├── Python 3.11+
    ├── Garak installation
    ├── Zhipu API key
    └── Basic LLM security knowledge
         ↓
Foundation (this directory)
    ├── 1. Prompt Injection - Start here for injection basics
    ├── 2. Jailbreaks - Learn safety guardrail bypasses
    ├── 3. Data Leakage - Understand training data extraction
    └── 4. Malicious Content - Test for harmful output
         ↓
Advanced Topics
    ├── Custom probe development
    ├── Detector customization
    ├── Enterprise deployment patterns
    └── CI/CD integration
```

**Recommended order:**
1. **Prompt Injection** - Foundational for understanding all LLM attacks
2. **Jailbreaks** - Builds on injection concepts with persona-based attacks
3. **Data Leakage** - Different attack vector (exfiltration vs. injection)
4. **Malicious Content** - Tests model output safety rather than input manipulation

---

## Quick Start Commands

### Installation

```bash
# Install Garak
uv pip install garak

# Verify installation
garak --version

# Set up environment
cp .env.example .env
# Edit .env to add your ZHIPU_API_KEY
```

### Running First Evaluation

```bash
# Navigate to prompt injection topic
cd src/garak_evaluation/advanced/prompt_injection

# Run with Python API (recommended)
python prompt_injection_test.py

# Or run with CLI
garak --model_type openai-compatible \
      --model_name glm-4-plus \
      --probe_type encoding.B64NestedInjection \
      --openai_base https://open.bigmodel.cn/api/paas/v4/ \
      --report_prefix prompt_injection_results

# Or run with YAML config
garak -c prompt_injection_cli.yaml
```

### Viewing Results

Results are saved in JSONL format in the `garak_results/` directory:

```bash
# View raw results
cat garak_results/prompt_injection_results.jsonl

# Analyze with Python script
cd src/garak_evaluation/advanced
python analyze_all.py
```

---

## Configuration Approaches

### 1. CLI-Based Execution

Simplest approach for quick tests:

```bash
garak --model_type openai-compatible \
      --model_name glm-4-plus \
      --probe_type dan.DAN \
      --openai_base https://open.bigmodel.cn/api/paas/v4/
```

### 2. YAML Configuration

For repeatable, version-controlled evaluations:

```yaml
generators:
  - type: openai-compatible
    name: glm-4-plus
    api_base: https://open.bigmodel.cn/api/paas/v4/

probes:
  - dan.DAN
  - grandma.Grandma

detectors:
  - all

report_prefix: jailbreaks_results
```

### 3. Python API

For programmatic evaluation and custom analysis:

```python
import garak.generators
import garak.probes

generator = garak.generators.Generator("glm-4-plus")
probe = garak.probes.Probe("dan.DAN")

results = probe.run(generator)
analysis = analyze_results(results)
```

---

## Result Interpretation

### Understanding Pass/Fail Rates

- **Pass rate**: Proportion of test cases that were rejected/defended
- **Fail rate**: Proportion of test cases that succeeded in attacking the model
- **Higher pass rate** = Better security posture
- **Lower pass rate** = Vulnerabilities detected

### Detector Scores

Garak uses multiple detectors to identify successful attacks:

- **Keyword-based**: Matches known malicious patterns
- **Classifier-based**: Uses ML models to detect attacks
- **Rule-based**: Applies heuristics and rules

### Severity Classification

| Severity | Fail Rate | Interpretation |
|----------|-----------|----------------|
| **HIGH** | >= 50% | Critical vulnerabilities requiring immediate attention |
| **MEDIUM** | 30-50% | Significant vulnerabilities that should be addressed |
| **LOW** | 10-30% | Minor vulnerabilities or edge cases |
| **MINIMAL** | < 10% | Acceptable security posture |

---

## Troubleshooting

### Issue: Garak installation fails

**Possible causes:**
1. Python version incompatible (requires 3.10+)
2. Network connectivity issues
3. Dependency conflicts

**Solution:**
```bash
# Check Python version
python --version  # Should be 3.10 or higher

# Clear cache and retry
uv pip install --upgrade pip
uv pip install garak --no-cache-dir

# Install with verbose output for debugging
uv pip install garak -v
```

### Issue: API key configuration problems

**Possible causes:**
1. ZHIPU_API_KEY not set in environment
2. Invalid API key format
3. API key expired

**Solution:**
```bash
# Check if API key is set
echo $ZHIPU_API_KEY

# Test API key
curl -X POST https://open.bigmodel.cn/api/paas/v4/chat/completions \
  -H "Authorization: Bearer $ZHIPU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"glm-4-plus","messages":[{"role":"user","content":"test"}]}'

# Reload environment
source .env
```

### Issue: Model connectivity issues

**Possible causes:**
1. Network blocking API access
2. Incorrect base URL
3. Rate limiting

**Solution:**
```bash
# Test connectivity
curl -I https://open.bigmodel.cn/api/paas/v4/

# Check base URL in config
# Should be: https://open.bigmodel.cn/api/paas/v4/

# Verify model name
# Valid options: glm-4-plus, glm-5-plus, glm-5-std
```

### Issue: JSONL parsing errors

**Possible causes:**
1. Corrupted results file
2. Invalid JSONL format
3. Incomplete evaluation run

**Solution:**
```bash
# Validate JSONL format
python -m json.tool garak_results/eval.jsonl

# Re-run evaluation
garak -c config.yaml --report_prefix new_eval

# Check for error messages in terminal output
```

### Issue: All probes failing

**Possible causes:**
1. Model refusing all requests (over-safe)
2. Generator configuration incorrect
3. Probe parameters not matching model capabilities

**Solution:**
```bash
# Test basic model access first
garak --model_type openai-compatible \
      --model_name glm-4-plus \
      --probe_type continuation.Continuation \
      --openai_base https://open.bigmodel.cn/api/paas/v4/

# Try a different probe to isolate the issue
# Use simple probes first: continuation, repeat
```

---

## Next Steps

After mastering these tutorials:

1. **Production Integration:**
   - Set up CI/CD security testing with Garak
   - Configure automated regression testing
   - Establish performance baselines and alerting

2. **Custom Development:**
   - Build domain-specific probes
   - Create custom detectors for your use cases
   - Integrate with existing security workflows

3. **Advanced Topics:**
   - Enterprise deployment patterns (multi-tenant, RBAC)
   - Real-time monitoring dashboards
   - Automated remediation workflows

---

## Related Resources

- [Garak Documentation](https://github.com/NVIDIA/garak)
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Zhipu AI API](https://open.bigmodel.cn/)
- [CPH Sec Red Teaming Guide](https://cphsec.mercury.ai/red-teaming/)

---

## Additional Topics

The advanced directory may be expanded with additional topics:

- `model_extraction/` - Model theft and extraction attacks
- `adversarial_robustness/` - Adversarial example testing
- `bias_stereotype/` - Bias and stereotype amplification detection
- `hallucination_detection/` - Factuality and hallucination testing

---

## Contributing

When adding new topics:

1. Follow the established directory structure
2. Include README, YAML config, Python runner, and test cases
3. Map to OWASP LLM Top 10 category
4. Document CPH Sec lifecycle phase alignment
5. Include screenshot placeholders for visual documentation
