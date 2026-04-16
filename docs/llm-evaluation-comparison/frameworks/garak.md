# Garak Framework Profile

Comprehensive profile of Garak (Generative AI Red-teaming & Assessment Kit), NVIDIA's LLM vulnerability scanner.

## Architecture Overview

Garak is a **Python-based security testing framework** designed specifically for identifying vulnerabilities in Large Language Models. It uses a **probe/detector system** to systematically test LLMs for known attack patterns and security weaknesses.

### Core Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         GARAK FRAMEWORK                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   PROBES     │      │  DETECTORS    │      │  GENERATORS  │  │
│  │              │      │              │      │              │  │
│  │ Attack payloads│ ───> │ Analyze      │ ───> │ Connect to   │  │
│  │ for testing  │      │ responses    │      │ any LLM API  │  │
│  │              │      │ for success  │      │              │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         │                     │                   │              │
│         v                     v                   v              │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    HARNESS                               │  │
│  │  • Probewise execution  • Result aggregation             │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                 ↓                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                 REPORTING & ANALYSIS                      │  │
│  │  • Pass/fail rates  • Severity classification           │  │
│  │  • Vulnerability patterns  • JSONL logging               │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Design Philosophy

- **Vulnerability-focused**: Tests for known LLM vulnerabilities and attack patterns
- **Research-backed**: Probes based on academic research and documented exploits
- **Systematic**: Organized approach to security assessment with probe categories
- **Extensible**: Plugin system for custom probes, detectors, and generators

## Core Features

### Probe-Based Testing

Garak organizes security tests into **probe categories**, each containing specific attack patterns:

| Probe Category | What It Tests | Example Attacks |
|----------------|---------------|-----------------|
| **promptinject** | Input manipulation | Encoded commands, HTML injection, JSON overrides |
| **dan** | Jailbreaks | DAN prompts, role-play attacks, persona adoption |
| **encoding** | Text encoding bypasses | Base64, quoted-printable, MIME encoding |
| **malwaregen** | Malware generation | Malicious code, dangerous instructions |
| **packagehallucination** | Package hallucination | Non-existent package references |
| **xss** | Cross-site scripting | XSS attack vectors |
| **continuation** | Harmful completion | Continuing toxic or harmful content |
| **atkgen** | Automated attack generation | AI-powered attack generation |

### Detector System

Detectors analyze model responses to determine if an attack succeeded:

| Detector Type | How It Works | What It Catches |
|---------------|--------------|-----------------|
| **Keyword** | Pattern matching on known malicious phrases | Explicit attack confirmations |
| **Classifier** | ML models trained on attack patterns | Subtle, contextual attacks |
| **Rule-based** | Heuristics and linguistic analysis | Encoding, structural anomalies |
| **AlwaysPass** | Testing utility (always passes) | For testing detector logic |
| **AlwaysFail** | Testing utility (always fails) | For testing detector logic |

### Generator Support

Garak supports connecting to virtually any LLM:

- **OpenAI-Compatible**: Any API following OpenAI's format
- **Hugging Face**: Both local models and Inference API
- **AWS Bedrock**: Anthropic Claude, Meta Llama, Amazon Titan, AI21, Cohere, Mistral
- **Replicate**: Public and private endpoints
- **Cohere**: Command and Command Light models
- **Groq**: Fast inference API
- **NVIDIA NIM**: Models from build.nvidia.com
- **REST**: Generic REST API support via YAML configuration
- **Local Models**: gguf models via llama.cpp

## Configuration Options

### Basic Command Line Usage

```bash
# Basic syntax
garak --target_type <type> --target_name <model> --probes <probes>

# Example: Test OpenAI GPT-4 for prompt injection
export OPENAI_API_KEY=sk-...
python -m garak --target_type openai --target_name gpt-4 --probes promptinject

# Example: Test Hugging Face model for jailbreaks
python -m garak --target_type huggingface --target_name gpt2 --probes dan

# Example: Run all probes
python -m garak --target_type openai --target_name gpt-4 --probes all
```

### Configuration via YAML

```yaml
# garak_config.yaml
generators:
  - type: openai
    name: gpt-4
    api_key_env_var: OPENAI_API_KEY

probes:
  - promptinject
  - dan
  - encoding
  - malwaregen

detectors:
  - keyword
  - classifier

output:
  format: jsonl
  report_prefix: security_scan
```

### Probe Selection

```bash
# List all available probes
python -m garak --list_probes

# Run specific probe family
python -m garak --probes promptinject

# Run specific probe
python -m garak --probes promptinject.ProbeInjectIndependent

# Run multiple probes
python -m garak --probes promptinject,dan,encoding

# Exclude specific probes
python -m garak --probes all --exclude_probes atkgen
```

## OWASP LLM Top 10 Coverage

Garak provides comprehensive coverage of the OWASP LLM Top 10 vulnerability categories:

| OWASP Category | Garak Coverage | Probes |
|----------------|----------------|--------|
| **LLM01: Prompt Injection** | Extensive | promptinject, encoding, gcg |
| **LLM02: Insecure Output Handling** | Good | xss, continuation |
| **LLM03: Training Data Poisoning** | Limited | leakreplay, misleading |
| **LLM04: Model Denial of Service** | Limited | Resource consumption tests |
| **LLM05: Supply Chain Vulnerabilities** | Good | packagehallucination |
| **LLM06: Sensitive Information Disclosure** | Extensive | leakreplay, donotanswer |
| **LLM07: Insecure Plugin Design** | Limited | Plugin-specific probes |
| **LLM08: Excessive Agency** | Moderate | Agent-focused probes |
| **LLM09: Overreliance** | Good | Hallucination detection |
| **LLM10: Model Theft** | Limited | Model extraction probes |

For detailed OWASP coverage mapping, see: [OWASP Coverage Comparison](../comparisons/owasp-coverage.md)

## Integration Capabilities

### CI/CD Integration

```bash
# In CI/CD pipeline
python -m garak --target_type openai --target_name $MODEL_NAME \
    --probes promptinject,dan,encoding \
    --report_prefix ci_test_$BUILD_NUMBER

# Check exit code for pass/fail
if [ $? -ne 0 ]; then
    echo "Security tests failed"
    exit 1
fi
```

### Reporting and Analysis

Garak generates multiple types of logs:

- **garak.log**: Debugging information continued across runs
- **JSONL report**: Structured report of current run (one per execution)
- **Hit log**: Detailed log of attempts that yielded vulnerabilities

### AI Vulnerability Database

Garak can optionally push findings to the AI Vulnerability Database for community tracking.

## Current Version Capabilities

### Key Strengths

1. **Comprehensive security coverage**: Probes for all major LLM vulnerability types
2. **Research-backed**: Attacks based on academic research and documented exploits
3. **Provider-agnostic**: Works with virtually any LLM API
4. **Python-native**: Pure Python implementation for easy integration
5. **Systematic approach**: Organized probe categories for thorough assessment

### Limitations

1. **Static attack library**: Primarily uses known exploits (limited dynamic generation)
2. **No quality metrics**: Focuses on security, not response quality
3. **Limited RAG testing**: Doesn't dive deep into RAG-specific security issues
4. **Security-focused**: Not suitable for general LLM quality testing

## When to Use Garak

### Ideal For

- **Security teams** conducting vulnerability assessments
- **Red team operations** against LLM applications
- **Regulatory compliance** requiring OWASP LLM Top 10 coverage
- **Python-first teams** preferring Python tools
- **Audit-style evaluations** with comprehensive reporting
- **Model comparison** from security perspective

### Less Ideal For

- Application-specific testing requiring custom attack generation
- RAG quality evaluation (use RAGas instead)
- Teams needing CI/CD-first workflows (Promptfoo may be better)
- General LLM quality testing beyond security

## Technical Requirements

### Installation

```bash
# Standard pip install
python -m pip install -U garak

# Development version from GitHub
python -m pip install -U git+https://github.com/NVIDIA/garak.git@main

# From source
git clone https://github.com/NVIDIA/garak.git
cd garak
python -m pip install -e .
```

### Dependencies

- **Python**: 3.10-3.12
- **Package manager**: pip
- **Key dependencies**: transformers, openai, anthropic, langchain (varies by generator)

### Environment Variables

```bash
# LLM Provider API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
COHERE_API_KEY=...
REPLICATE_API_TOKEN=...
GROQ_API_KEY=...

# AWS Bedrock
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION_NAME=...

# Hugging Face
HF_TOKEN=...  # For private models

# Optional: Garak settings
GARAKLogLevel=INFO
```

## Related Resources

### Official Documentation

- **Main Docs**: https://garak.readthedocs.io/
- **GitHub**: https://github.com/NVIDIA/garak
- **Project Site**: https://garak.ai
- **Paper**: "garak: A Framework for Security Probing Large Language Models" (arXiv)

### Project Tutorials

- **Garak Tutorial**: [@src/garak_evaluation/advanced/README.md](../../src/garak_evaluation/advanced/README.md)
  - OWASP LLM Top 10 coverage
  - Probe/detector system explanation
  - Working examples with Zhipu AI

### Related Comparisons

- **vs Promptfoo**: [Existing Comparison](../../references/promptfoo/site/blog/promptfoo-vs-garak.md)
- **OWASP Coverage**: [Detailed OWASP Mapping](../comparisons/owasp-coverage.md)
- **Feature Matrix**: [Feature Comparison Matrix](../comparisons/feature-matrix.md)
