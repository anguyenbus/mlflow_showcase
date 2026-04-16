# LLM Evaluation Framework Comparison Guide

Comprehensive decision-support resource for comparing Promptfoo, Garak, and RAGas evaluation frameworks. This guide helps AI developers, ML engineers, security teams, and technical decision makers choose the right evaluation framework(s) through detailed comparisons, decision frameworks, and implementation guidance.

## Goal

This guide provides detailed analysis of three leading LLM evaluation frameworks to help you:

- Select frameworks that match your specific use cases and technical requirements
- Understand the strengths, limitations, and complementarity of each tool
- Design hybrid evaluation strategies using multiple frameworks
- Implement comprehensive evaluation coverage without tool proliferation

## Target Audience

### For Technical Implementers

Engineers implementing LLM applications will find:
- Configuration details and examples for each framework
- Integration patterns for CI/CD pipelines
- Technical requirements and dependencies
- Code examples and working configurations

### For Decision Makers

Engineering managers and architects will find:
- Feature comparisons and capability analysis
- Cost/benefit considerations for framework adoption
- Team expertise requirements
- Use case-based recommendations

## Quick Navigation

### By Use Case

- **RAG Systems**: Start with [RAG Evaluation Comparison](evaluation-domains/rag-evaluation.md) and [RAGas Framework Profile](frameworks/ragas.md)
- **Security Testing**: Start with [Security Evaluation Comparison](evaluation-domains/security-evaluation.md) and [OWASP Coverage](comparisons/owasp-coverage.md)
- **General Quality Testing**: Start with [Promptfoo Framework Profile](frameworks/promptfoo.md) and [Use Case Mapping](comparisons/use-case-mapping.md)
- **CI/CD Integration**: Start with [CI/CD Integration Guide](integration/cicd-integration.md)

### By Framework

- **Promptfoo**: CLI-based testing for prompts, models, and RAGs - [Full Profile](frameworks/promptfoo.md)
- **Garak**: NVIDIA's LLM vulnerability scanner - [Full Profile](frameworks/garak.md)
- **RAGas**: Python-based RAG evaluation toolkit - [Full Profile](frameworks/ragas.md)

### By Decision Need

- **Not sure which framework to choose?**: Start with [Decision Framework](decision-support/decision-framework.md)
- **Need quick comparison?**: See [Feature Matrix](comparisons/feature-matrix.md) or [Quick Reference](decision-support/quick-reference.md)
- **Planning integration?**: See [Technical Requirements](integration/technical-requirements.md)

## Framework Overview

| Framework | Primary Focus | Language | Best For |
|-----------|--------------|----------|----------|
| **Promptfoo** | Prompt testing, model comparison, red teaming | TypeScript/Node.js | CI/CD integration, application-specific testing |
| **Garak** | Security vulnerability scanning | Python | OWASP LLM Top 10 coverage, security audits |
| **RAGas** | RAG evaluation metrics | Python | Retrieval quality, answer faithfulness, context metrics |

## Key Findings Summary

### Complementarity

These frameworks serve different primary purposes and can be complementary:

- **Promptfoo + RAGas**: Combine prompt engineering with RAG-specific metrics for comprehensive RAG system evaluation
- **Garak + Promptfoo**: Curated vulnerability probes (Garak) plus dynamic attack generation (Promptfoo) for security testing
- **All Three**: End-to-end evaluation covering security, quality, and RAG-specific metrics

### Decision Heuristics

1. **Choose Promptfoo if**: You need CI/CD integration, application-specific testing, or model comparison
2. **Choose Garak if**: You need comprehensive OWASP LLM Top 10 security coverage
3. **Choose RAGas if**: You're building RAG systems and need retrieval/faithfulness metrics
4. **Combine frameworks if**: You need comprehensive coverage across multiple evaluation domains

## Directory Structure

```
docs/llm-evaluation-comparison/
├── README.md                               # This file - guide overview
├── frameworks/                             # Framework deep dives
│   ├── promptfoo.md                        # Promptfoo profile
│   ├── garak.md                            # Garak profile
│   └── ragas.md                            # RAGas profile
├── comparisons/                            # Comparison matrices
│   ├── feature-matrix.md                   # Feature comparison
│   ├── owasp-coverage.md                   # OWASP LLM Top 10 mapping
│   └── use-case-mapping.md                 # Use case recommendations
├── evaluation-domains/                     # Domain-specific analysis
│   ├── rag-evaluation.md                   # RAG evaluation comparison
│   └── security-evaluation.md              # Security testing comparison
├── integration/                            # Implementation guidance
│   ├── technical-requirements.md           # Tech stack requirements
│   ├── cicd-integration.md                 # CI/CD patterns
│   └── hybrid-solutions.md                 # Multi-framework integration
├── decision-support/                       # Decision tools
│   ├── decision-framework.md               # Decision flowchart
│   └── quick-reference.md                  # Scannable reference
└── examples/                               # Working configurations
    ├── promptfoo-examples.yaml             # Promptfoo examples
    ├── garak-examples.yaml                 # Garak examples
    ├── ragas-examples.yaml                 # RAGas examples
    └── hybrid-examples/                    # Multi-framework examples
        ├── promptfoo-ragas.yaml            # Promptfoo + RAGas
        └── garak-promptfoo.yaml            # Garak + Promptfoo
```

## Related Resources

### Existing Project Tutorials

This guide references existing implementation tutorials:

- **Promptfoo Tutorial**: [@src/promptfoo_evaluation/README.md](../../src/promptfoo_evaluation/README.md) - Comprehensive Promptfoo examples with Zhipu AI models
- **Garak Tutorial**: [@src/garak_evaluation/advanced/README.md](../../src/garak_evaluation/advanced/README.md) - Garak security evaluation with OWASP coverage
- **RAGas Tutorial**: [@src/ragas_evaluation/](../../src/ragas_evaluation/) - RAG evaluation with MLflow integration
- **Existing Comparison**: [@references/promptfoo/site/blog/promptfoo-vs-garak.md](../../references/promptfoo/site/blog/promptfoo-vs-garak.md) - Promptfoo vs Garak comparison

### External Documentation

- **Promptfoo**: https://promptfoo.dev/docs/
- **Garak**: https://garak.readthedocs.io/
- **RAGas**: https://docs.ragas.io/
- **OWASP LLM Top 10**: https://genai.owasp.org/llm-top-10/

## How to Use This Guide

1. **Start with your use case**: Identify what you're trying to evaluate (RAG system, security, general quality)
2. **Review the decision framework**: Use the decision tree to narrow down framework options
3. **Read framework profiles**: Understand the capabilities and requirements of recommended frameworks
4. **Check comparisons**: Verify feature coverage and use case alignment
5. **Review examples**: Examine working configurations for your scenario
6. **Plan integration**: Follow integration guidance for your chosen framework(s)

## Version Scope

This guide covers **current stable versions only** of each framework. Historical context about framework evolution is out of scope.

## Coverage

- **Frameworks**: Promptfoo, Garak, RAGas
- **Security Standards**: OWASP LLM Top 10 only
- **Evaluation Domains**: Security testing, RAG evaluation, quality metrics
- **Integration**: CI/CD, MLflow, observability platforms

## Feedback and Contributions

This guide is part of the tracing project's documentation suite. For feedback or suggestions, refer to the project's contribution guidelines.
