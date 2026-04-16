# Promptfoo Framework Profile

Comprehensive profile of Promptfoo, a CLI-based LLM evaluation framework for testing prompts, models, and RAG systems.

## Architecture Overview

Promptfoo is a **CLI-based evaluation framework** built with TypeScript and Node.js. It uses a declarative YAML/JSON configuration approach to define tests, models, and evaluation criteria.

### Core Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PROMPTFOO FRAMEWORK                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   PROVIDERS  │      │  ASSERTIONS  │      │  STRATEGIES  │  │
│  │              │      │              │      │              │  │
│  │ OpenAI, Anth│ropic,│ Model-graded,│ Pattern-based,  │  │
│  │ Local, Custom│      │ Python, JS   │ red-team gen.  │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         │                       │                    │          │
│         └───────────────────────┴────────────────────┘          │
│                                 ↓                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    EVALUATION ENGINE                     │  │
│  │  • Test execution  • Result comparison  • Reporting      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                 ↓                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    OUTPUT OPTIONS                        │  │
│  │  • CLI output  • Web UI  • JSON export  • CI/CD logs     │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Design Philosophy

- **Configuration-as-code**: All tests defined in YAML/JSON for version control and CI/CD
- **Provider-agnostic**: Works with any LLM provider through flexible provider system
- **Extensible assertions**: Multiple assertion types including model-graded evaluations
- **CI/CD-first**: Designed for automated testing in development pipelines

## Core Features

### Prompt Testing

- **Declarative test configuration**: Define tests in YAML with prompts, variables, and expected outcomes
- **Assertion types**:
  - Exact match and similarity matching
  - Model-graded assertions (LLM-as-judge)
  - Python and JavaScript custom assertions
  - Regex pattern matching
  - JSON schema validation
- **Variable interpolation**: Dynamic prompt generation from test data

### Model Comparison

- **Side-by-side comparison**: Test multiple models simultaneously
- **A/B testing**: Compare prompt variants across models
- **Performance metrics**: Latency, token usage, cost tracking
- **Visual comparison**: Web UI for comparing model outputs

### Red Teaming and Security

- **Dynamic attack generation**: AI-powered generation of contextually relevant attacks
- **Specialized plugins**:
  - RAG security testing (context injection, access control, data poisoning)
  - Agent security testing (RBAC, tool misuse, API fuzzing)
  - Prompt injection variants
- **Compliance mapping**: OWASP, NIST, MITRE ATLAS, EU AI Act

### RAG Evaluation

- **RAG-specific plugins**: Dedicated security testing for retrieval-augmented generation
- **Context injection testing**: Tests for malicious content in retrieved documents
- **Access control validation**: Tests for document leakage beyond user permissions
- **Data poisoning detection**: Tests for corrupted knowledge base entries

### CI/CD Integration

- **GitHub Actions**: Native integration with automated workflows
- **CLI-first design**: Easy to integrate into any CI/CD pipeline
- **Exit codes**: Proper status codes for test failures
- **Output formats**: JSON, Markdown, HTML for reporting

## Configuration Options

### Basic Configuration Structure

```yaml
# promptfooconfig.yaml
description: My evaluation suite
prompts:
  - System prompt 1
  - System prompt 2

providers:
  - openai:gpt-4
  - anthropic:messages:claude-3-sonnet-20240229
  - id: custom-provider
    config:
      baseURL: https://api.example.com

tests:
  - description: Test case 1
    vars:
      query: What is X?
    assert:
      - type: contains
        value: expected output

# Optional: Default settings for all tests
defaultTest:
  assert:
    - type: javascript
      value: "output.toLowerCase().includes('answer')"
```

### Provider Configuration

Promptfoo supports a wide range of LLM providers:

- **Major Providers**: OpenAI, Anthropic, Azure OpenAI, Google, AWS Bedrock
- **Open-Source Models**: Ollama, vLLM, LocalAI, LM Studio
- **Custom Providers**: REST APIs, Python scripts, any HTTP endpoint
- **Provider Options**: Temperature, max tokens, headers, auth

### Assertion Types

| Assertion Type | Description | Use Case |
|----------------|-------------|----------|
| `contains` | Output contains specified text | Basic validation |
| `icontains` | Case-insensitive contains | Flexible text matching |
| `matches` | Regex pattern matching | Format validation |
| `json` | JSON schema validation | Structured output |
| `javascript` | Custom JS evaluation | Complex logic |
| `python` | Custom Python evaluation | Python-based assertions |
| `llm-rubric` | Model-graded quality | Subjective quality |
| `similar` | Embedding similarity | Semantic matching |
| `is-json` | Valid JSON check | JSON outputs |
| `cost` | Cost threshold | Budget validation |
| `latency` | Performance check | Speed requirements |

## Plugin Ecosystem

### Red Team Plugins

Promptfoo's red team capabilities include:

- **Attack strategies**: Automated generation of adversarial prompts
- **RAG security**: Specialized testing for retrieval systems
- **Agent testing**: Multi-turn attack scenarios for agents
- **Compliance mapping**: Results mapped to security standards

### Custom Assertions

- **JavaScript assertions**: Write custom validation logic in JS
- **Python assertions**: Write custom validation logic in Python
- **Webhook assertions**: Call external services for validation
- **Model-graded assertions**: Use LLMs to evaluate output quality

### Extensibility

- **Custom providers**: Add support for any LLM API
- **Custom evaluators**: Implement custom grading logic
- **Plugin system**: Extend functionality through plugins
- **CLI extensions**: Add custom CLI commands

## Integration Capabilities

### CI/CD Integration

**GitHub Actions Example:**

```yaml
# .github/workflows/llm-eval.yml
name: LLM Evaluation
on: [pull_request]
jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install promptfoo
        run: npm install -g promptfoo
      - name: Run evaluation
        run: promptfoo eval --config promptfooconfig.yaml
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### MLflow Integration

Promptfoo can export results compatible with MLflow tracking:

- **Experiment tracking**: Log evaluation results as MLflow runs
- **Parameter logging**: Model configurations and test parameters
- **Metric tracking**: Assertion results and performance metrics
- **Artifact storage**: Save evaluation outputs as artifacts

For detailed MLflow integration patterns, see: [@src/promptfoo_evaluation/](../../src/promptfoo_evaluation/)

### Observability Platforms

- **Export formats**: JSON, CSV for external analysis
- **Webhook notifications**: Send results to monitoring systems
- **Custom reporters**: Build custom integrations via reporter plugins

## Current Version Capabilities

### Key Strengths

1. **Application-specific testing**: Generates attacks tailored to your specific application context
2. **RAG security coverage**: Unique testing capabilities for RAG-specific vulnerabilities
3. **Agent security**: Multi-turn testing for agentic applications
4. **CI/CD native**: Designed from the ground up for automated testing
5. **Compliance reporting**: Ready-to-share reports mapped to security standards

### Limitations

1. **Node.js ecosystem**: Primarily JavaScript/TypeScript focused (Python available via providers)
2. **RAG quality metrics**: Focuses on RAG security, not quality metrics like faithfulness
3. **Model-graded assertions**: Requires additional LLM API calls for evaluation
4. **Learning curve**: YAML configuration complexity for advanced scenarios

## When to Use Promptfoo

### Ideal For

- Teams with **CI/CD infrastructure** needing automated testing
- **Application-specific testing** requiring custom attack generation
- **RAG systems** needing security validation
- **Agent applications** requiring multi-turn security testing
- Teams with **JavaScript/TypeScript expertise**
- **Model comparison** and A/B testing scenarios

### Less Ideal For

- Pure Python teams without Node.js experience
- RAG quality evaluation (use RAGas instead)
- Security-focused teams needing only vulnerability scanning (Garak may be simpler)
- Projects requiring minimal configuration overhead

## Technical Requirements

### Installation

```bash
# Global installation
npm install -g promptfoo

# Or via brew
brew install promptfoo

# Or via pip (Python wrapper)
pip install promptfoo

# Or use npx (no installation)
npx promptfoo@latest eval
```

### Dependencies

- **Node.js**: ^20.20.0 || >=22.22.0
- **Package managers**: npm, pnpm, yarn supported
- **Python**: Optional, for Python-based assertions (3.11+)

### Environment Variables

```bash
# Provider API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
AZURE_OPENAI_API_KEY=...
AWS Bedrock credentials via AWS CLI

# Promptfoo settings
PROMPTFOO_DISABLE_REMOTE_GENERATION=true  # Disable remote generation
PROMPTFOO_CACHE_DIR=custom/cache/path     # Custom cache location
```

## Related Resources

### Official Documentation

- **Main Docs**: https://promptfoo.dev/docs/
- **Red Team Guide**: https://promptfoo.dev/docs/red-team/
- **Configuration Schema**: https://promptfoo.dev/docs/configuration/
- **Provider Reference**: https://promptfoo.dev/docs/providers/

### Project Tutorials

- **Promptfoo Tutorial**: [@src/promptfoo_evaluation/README.md](../../src/promptfoo_evaluation/README.md)
  - Zhipu AI GLM model integration
  - MLflow integration patterns
  - Working YAML examples

### Related Comparisons

- **vs Garak**: [OWASP Coverage](../comparisons/owasp-coverage.md)
- **vs RAGas**: [RAG Evaluation Comparison](../evaluation-domains/rag-evaluation.md)
- **Feature Matrix**: [Feature Comparison Matrix](../comparisons/feature-matrix.md)
