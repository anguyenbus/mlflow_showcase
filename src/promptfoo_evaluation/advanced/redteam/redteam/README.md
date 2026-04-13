# Red Team Evaluation

Comprehensive red team evaluation module for systematically testing LLM applications against adversarial attacks including prompt injection, jailbreaking, harmful content generation, and RAG security vulnerabilities.

## Overview

Red team evaluation is a critical practice for AI safety that involves simulating adversarial attacks to identify security vulnerabilities before they can be exploited in production. This module leverages promptfoo's built-in red team capabilities to provide:

- **Prompt Injection Testing**: Detects attempts to manipulate the model through injected instructions
- **Jailbreaking Detection**: Identifies multi-turn strategies designed to bypass safety protocols
- **Harmful Content Evaluation**: Tests refusal behavior for prohibited content categories
- **RAG Security Testing**: Validates role-based access controls and data exfiltration prevention

## Why Red Team Testing Matters

AI systems face evolving security threats that traditional testing methods often miss. Red team evaluation provides:

1. **Proactive Security Discovery**: Find vulnerabilities before malicious actors do
2. **Regulatory Compliance**: Meet safety requirements for AI deployment
3. **Model Comparison**: Compare security posture across different model versions
4. **Guardrail Validation**: Test effectiveness of safety interventions

## Quick Start

### Prerequisites

- Zhipu AI API key (get from https://open.bigmodel.cn/)
- Node.js and npm installed (for promptfoo)
- Python 3.11+ with dependencies installed

### Setup

1. Set your API key:
   ```bash
   export ZHIPU_API_KEY=your_api_key_here
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Verify promptfoo installation:
   ```bash
   npx promptfoo --version
   ```

### Running Your First Evaluation

Run all red team tests:
```bash
python redteam_test.py --test-type=all
```

Run specific test types:
```bash
python redteam_test.py --test-type=injection
python redteam_test.py --test-type=jailbreaking
python redteam_test.py --test-type=guardrails
python redteam_test.py --test-type=rag_security
```

### Viewing Results

Launch the promptfoo web UI:
```bash
npx promptfoo view
```

View MLflow tracking:
```bash
mlflow ui
# Navigate to http://localhost:5000
```

## Plugin Reference

This module uses promptfoo's built-in red team plugins:

### Prompt Injection Plugins

| Plugin | Description |
|--------|-------------|
| `indirect-prompt-injection` | Tests injection through contextual data |
| `prompt-extraction` | Attempts to extract system prompts |
| `goal-hijacking` | Tests redirection of model objectives |

### Jailbreaking Plugins

| Plugin | Description |
|--------|-------------|
| `jailbreak:composite` | Combines multiple jailbreak techniques |
| `jailbreak:tree` | Systematic exploration of jailbreak attempts |
| `crescendo` | Gradual escalation of inappropriate requests |
| `mischievous-user` | Role-based attacks pretending to be authorized users |

### Harmful Content Plugins

| Plugin | Description |
|--------|-------------|
| `harmful:hate` | Tests hate speech generation |
| `harmful:self-harm` | Tests self-harm content refusal |
| `harmful:violent-crime` | Tests violent content refusal |
| `harmful:sexual-content` | Tests sexual content refusal |

### RAG Security Plugins

| Plugin | Description |
|--------|-------------|
| `rbac` | Tests role-based access control bypass |
| `pii` | Tests PII leakage prevention |
| `cross-session-leak` | Tests cross-session data isolation |
| `data-exfil` | Tests data exfiltration attempts |
| `rag-poisoning` | Tests context injection attacks |

## Strategy Guide

### Attack Strategies

This module includes several attack strategies:

1. **Jailbreak Templates**: Uses known jailbreak patterns to test bypass detection
2. **Crescendo**: Multi-turn attacks that gradually push boundaries
3. **Mischievous User**: Pretends to be a trusted user to bypass restrictions
4. **Encoding Obfuscation**: Attempts to bypass filters using encoding

### Configuration

Each test type has its own configuration in the respective subdirectory:

- `prompt_injection/prompt_injection.yaml`: Prompt injection tests
- `jailbreaking/jailbreaking.yaml`: Jailbreak strategy tests
- `guardrails/guardrails.yaml`: Harmful content refusal tests
- `rag_security/rag_security.yaml`: RAG-specific security tests

## Results Interpretation

### Security Metrics

| Metric | Description | Good Range |
|--------|-------------|------------|
| Guardrail Effectiveness | Percentage of attacks blocked | >80% |
| Attack Success Rate | Percentage of successful attacks | <20% |
| Vulnerability Count | Number of failed tests | 0-2 |
| Refusal Rate | Percentage of harmful requests refused | >60% |

### Per-Category Breakdown

Results include effectiveness scores for each attack category:
- **Injection Effectiveness**: Success against prompt injection
- **Jailbreaking Effectiveness**: Success against jailbreak attempts
- **Harmful Content Effectiveness**: Success against harmful content generation
- **PII Effectiveness**: Success against PII leakage

## Security Fix Prioritization

When vulnerabilities are found, prioritize fixes based on severity:

### Critical Severity
- **Attack Success Rate >50%**: Immediate remediation required
- **Guardrail Effectiveness <50%**: Fundamental safety failure
- **Jailbreaking Success**: Core bypass vulnerabilities

**Action**: Block model deployment until fixed.

### High Severity
- **Attack Success Rate 30-50%**: Significant vulnerabilities
- **PII Leakage Potential**: Data privacy risk
- **Injection Success**: Prompt manipulation capability

**Action**: Fix within 1-2 sprints before production deployment.

### Medium Severity
- **Attack Success Rate 10-30%**: Moderate vulnerabilities
- **Specific Category Failures**: Limited scope issues
- **Refusal Rate <50%**: Insufficient safety responses

**Action**: Address in next development cycle.

### Low Severity
- **Attack Success Rate <10%**: Minor vulnerabilities
- **Edge Case Failures**: Unlikely real-world scenarios

**Action**: Monitor and address during regular maintenance.

### Recommended Remediation Order

1. Fix jailbreak bypasses (highest exploitation risk)
2. Address prompt injection vulnerabilities (most common attack)
3. Improve harmful content refusal (regulatory risk)
4. Hardening RAG security (data protection)
5. Optimize refusal messaging (user experience)

## Configuration Details

### Model Configuration

Default model: `glm-4.6` (Zhipu AI via OpenAI-compatible API)

Base URL: `https://open.bigmodel.cn/api/paas/v4/`

### Environment Variables

- `ZHIPU_API_KEY`: Required API key for model access
- `OPENAI_API_KEY`: Set to ZHIPU_API_KEY for promptfoo compatibility
- `OPENAI_BASE_URL`: Set to Zhipu AI base URL
- `PROMPTFOO_DISABLE_REMOTE_GENERATION`: Set to `false` to enable plugin test generation

## Subdirectories

- **prompt_injection/**: Prompt injection-specific tests and configuration
- **jailbreaking/**: Multi-turn jailbreak strategy tests
- **guardrails/**: Harmful content and guardrail evaluation
- **rag_security/**: RAG system security and access control tests

See individual README files in each subdirectory for detailed information.

## Troubleshooting

### Common Issues

**Issue**: "ZHIPU_API_KEY not set"
- **Solution**: Export the environment variable or add to `.env` file

**Issue**: "promptfoo not found"
- **Solution**: Install with `npm install -g promptfoo` or use `npx promptfoo`

**Issue**: "Exit code 100"
- **Note**: This is expected when tests fail - it's not an error

**Issue**: High vulnerability count
- **Solution**: Review Security Fix Prioritization section above

## Additional Resources

- [promptfoo Red Team Documentation](https://promptfoo.dev/docs/red-team/)
- [Zhipu AI API Documentation](https://open.bigmodel.cn/dev/api)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
