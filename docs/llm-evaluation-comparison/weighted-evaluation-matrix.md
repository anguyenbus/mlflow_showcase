# LLM Evaluation Framework - Weighted Evaluation Matrix

A quantitative comparison framework for selecting between Promptfoo, RAGas, and Garak based on weighted scoring across key evaluation criteria.

## Scoring Scale (1-5)

| Score | Rating | Description |
|-------|--------|-------------|
| **5** | Excellent | Comprehensive, best-in-class capability |
| **4** | Very Good | Strong support with minor gaps |
| **3** | Good | Meets baseline needs |
| **2** | Fair | Partial support, requires heavy customization |
| **1** | Poor | Does not meet expectation / Not supported |

---

## Evaluation Matrix

| Category | Criteria | Weight % | Promptfoo Score | Weighted Score | RAGas Score | Weighted Score | Garak Score | Weighted Score |
|----------|----------|----------|-----------------|----------------|-------------|----------------|-------------|----------------|
| **Security Testing** | OWASP LLM Top 10 Coverage | 15% | 4 | 0.60 | 1 | 0.15 | 5 | 0.75 |
| **Security Testing** | Dynamic Attack Generation | 10% | 5 | 0.50 | 1 | 0.10 | 2 | 0.20 |
| **Security Testing** | Red Teaming Workflows | 10% | 5 | 0.50 | 1 | 0.10 | 4 | 0.40 |
| **RAG Evaluation** | Retrieval Quality Metrics | 10% | 2 | 0.20 | 5 | 0.50 | 1 | 0.10 |
| **RAG Evaluation** | Generation Quality Metrics | 10% | 2 | 0.20 | 5 | 0.50 | 1 | 0.05 |
| **RAG Evaluation** | RAG Security Testing | 8% | 5 | 0.40 | 1 | 0.08 | 2 | 0.16 |
| **CI/CD Integration** | Native Pipeline Support | 8% | 5 | 0.40 | 3 | 0.24 | 3 | 0.24 |
| **Provider Coverage** | LLM Provider Support | 7% | 5 | 0.35 | 3 | 0.21 | 5 | 0.35 |
| **Observability** | Monitoring & Reporting | 7% | 4 | 0.28 | 3 | 0.21 | 3 | 0.21 |
| **Usability** | Configuration Complexity | 8% | 3 | 0.24 | 4 | 0.32 | 3 | 0.24 |
| **Usability** | Documentation Quality | 5% | 4 | 0.20 | 4 | 0.20 | 3 | 0.15 |
| **Community** | Ecosystem & Extensibility | 2% | 4 | 0.08 | 3 | 0.06 | 3 | 0.06 |
| **TOTAL** | | **100%** | | **4.15** | | **2.87** | | **2.91** |

---

## Score Rationale

### Security Testing

| Criteria | Promptfoo | RAGas | Garak |
|----------|-----------|-------|-------|
| **OWASP LLM Top 10 (15%)** | **4/5 - Very Good** - Comprehensive coverage with explicit mapping for all 10 categories. Dynamic generation finds context-specific vulnerabilities. Minor gaps in some niche categories compared to Garak's specialized probes. | **1/5 - Poor** - No security testing capabilities. RAGas focuses exclusively on quality metrics, not vulnerability assessment. | **5/5 - Excellent** - Extensive probe coverage for all OWASP categories. Research-backed attacks based on academic exploits. Best-in-class for vulnerability scanning. |
| **Dynamic Attack Generation (10%)** | **5/5 - Excellent** - AI-powered attack generation tailored to specific application context. Creates contextually relevant adversarial prompts automatically. Best-in-class capability. | **1/5 - Poor** - Not applicable. No attack generation capabilities. | **2/5 - Fair** - Primarily uses curated/static attack library. Limited dynamic generation (atkgen probe exists but less sophisticated than Promptfoo). Requires manual probe selection. |
| **Red Teaming Workflows (10%)** | **5/5 - Excellent** - Purpose-built for red teaming with multi-turn agent testing, compliance reporting (NIST, MITRE ATLAS, EU AI Act). Export-ready reports for stakeholders. | **1/5 - Poor** - Not designed for red teaming. Focuses on quality assessment, not adversarial testing. | **4/5 - Very Good** - Designed for security assessments with systematic probe execution, severity classification, and vulnerability reporting. Minor gaps in polished reporting compared to Promptfoo. |

### RAG Evaluation

| Criteria | Promptfoo | RAGas | Garak |
|----------|-----------|-------|-------|
| **Retrieval Quality Metrics (10%)** | **2/5 - Fair** - Can test retrieval through custom assertions but lacks native metrics like context precision/recall. Requires significant manual implementation to match RAGas capabilities. | **5/5 - Excellent** - Purpose-built with context precision, context recall, and context entity recall metrics. Industry-standard RAG retrieval evaluation. Best-in-class. | **1/5 - Poor** - Can test retrieval security (access control, data poisoning) but does not measure retrieval quality. No metrics for precision/recall. |
| **Generation Quality Metrics (10%)** | **2/5 - Fair** - Model-graded assertions can evaluate quality indirectly, but lacks RAG-specific metrics like faithfulness and answer relevancy. Requires heavy customization. | **5/5 - Excellent** - Comprehensive metrics: faithfulness, answer relevancy, answer correctness, answer similarity. The gold standard for RAG generation evaluation. | **1/5 - Poor** - No generation quality metrics. Focuses exclusively on security vulnerabilities, not response quality assessment. |
| **RAG Security Testing (8%)** | **5/5 - Excellent** - Unique RAG security plugins for context injection, access control validation, and data poisoning detection. Most comprehensive RAG security coverage available. | **1/5 - Poor** - No security testing. Cannot detect RAG-specific vulnerabilities. | **2/5 - Fair** - Has some probes relevant to RAG (prompt injection, data leakage) but lacks specialized RAG security testing like context injection or access control validation. |

### CI/CD Integration

| Criteria | Promptfoo | RAGas | Garak |
|----------|-----------|-------|-------|
| **Native Pipeline Support (8%)** | **5/5 - Excellent** - Built from ground up for CI/CD. Native GitHub Actions integration, proper exit codes, YAML config in version control, declarative tests. | **3/5 - Good** - Can be integrated via Python scripts and MLflow, meets baseline needs but requires more custom setup. Not CI/CD-first by design. | **3/5 - Good** - CLI tool with exit codes enables CI/CD integration, but lacks native workflow integrations. Requires manual configuration similar to RAGas. |

### Provider Coverage

| Criteria | Promptfoo | RAGas | Garak |
|----------|-----------|-------|-------|
| **LLM Provider Support (7%)** | **5/5 - Excellent** - Broadest coverage: all major providers (OpenAI, Anthropic, Azure, Google, AWS), local models (Ollama, vLLM), custom REST/Python providers. | **3/5 - Good** - Supports major providers (OpenAI, Anthropic, Azure) and local models via LiteLLM/Hugging Face. Meets baseline needs but less extensive. | **5/5 - Excellent** - Very comprehensive: OpenAI, Hugging Face, full AWS Bedrock catalog, Replicate, Cohere, Groq, NVIDIA NIM, REST APIs, local models. Matches Promptfoo in coverage. |

### Observability

| Criteria | Promptfoo | RAGas | Garak |
|----------|-----------|-------|-------|
| **Monitoring & Reporting (7%)** | **4/5 - Very Good** - Web UI for visualization, multiple export formats (JSON/CSV/HTML), MLflow integration, webhook notifications. Most polished observability with minor gaps in advanced analytics. | **3/5 - Good** - MLflow integration, structured results, pandas export. Meets baseline needs for observability. | **3/5 - Good** - JSONL reports, hit logs, severity classification. Functional but less polished UI than Promptfoo. Meets security reporting needs. |

### Usability

| Criteria | Promptfoo | RAGas | Garak |
|----------|-----------|-------|-------|
| **Configuration Complexity (8%)** | **3/5 - Good** - YAML configuration is powerful but has learning curve. CLI-first design is familiar to DevOps. Meets baseline needs but requires upfront investment. | **4/5 - Very Good** - Simple Python API, familiar to data scientists. Programmatic interface is intuitive for Python users with minor documentation gaps. | **3/5 - Good** - CLI-based with probe selection. Straightforward for basic use, complex probe configuration for advanced scenarios similar to Promptfoo. |
| **Documentation Quality (5%)** | **4/5 - Very Good** - Comprehensive docs at promptfoo.dev with examples, red team guide, configuration reference. Active community. Minor gaps in advanced scenarios. | **4/5 - Very Good** - Well-documented at docs.ragas.io with tutorials and examples. Clear explanations of metrics. Strong for Python users. | **3/5 - Good** - Good documentation at garak.readthedocs.io and GitHub. Security-focused but less extensive than Promptfoo/RAGas. |

### Community

| Criteria | Promptfoo | RAGas | Garak |
|----------|-----------|-------|-------|
| **Ecosystem & Extensibility (2%)** | **4/5 - Very Good** - Active development, plugin system, custom providers/assertions, strong GitHub community. Minor gaps in third-party plugins compared to larger frameworks. | **3/5 - Good** - Active open-source project, LangChain/LlamaIndex integration, growing community. Meets baseline needs for ecosystem support. | **3/5 - Good** - NVIDIA-backed with plugin system, but smaller community than Promptfoo. Meets baseline needs for extensibility. |

---

## Interpretation Guide

### Overall Scores (5 points maximum)

| Framework | Total Score | Strength Profile |
|-----------|-------------|------------------|
| **Promptfoo** | **4.15 / 5.00** | Best all-around choice. Strong in security, CI/CD, and general testing. Limitations in RAG quality metrics (requires custom implementation). |
| **Garak** | **2.91 / 5.00** | Security specialist. Excellent for OWASP compliance and vulnerability scanning. Weak in RAG evaluation and general quality metrics. |
| **RAGas** | **2.87 / 5.00** | RAG specialist. Unmatched for RAG quality assessment. No security capabilities whatsoever. |

### Score Interpretation

| Score Range | Interpretation |
|-------------|----------------|
| **4.0 - 5.0** | **Strong Fit** - Framework aligns well with evaluated criteria |
| **3.0 - 3.9** | **Moderate Fit** - Framework meets baseline but has gaps |
| **2.0 - 2.9** | **Specialized Fit** - Framework excels in specific areas only |
| **Below 2.0** | **Poor Fit** - Framework does not meet requirements |

### Weight Adjustment Guidance

The default weights above assume a **general AI development team** with diverse needs. Adjust weights based on your priorities:

| Use Case | Recommended Weight Adjustments |
|----------|-------------------------------|
| **RAG Application Development** | Increase RAG Evaluation to 40%+, decrease Security to 10% |
| **Security/Compliance Focus** | Increase Security Testing to 50%+, decrease RAG Evaluation to 5% |
| **CI/CD Automation** | Increase CI/CD Integration to 20%, add weight to Performance |
| **Model Comparison Only** | Increase Provider Coverage to 15%, add Model Comparison criteria |

### Decision Framework

| Scenario | Recommendation | Rationale |
|----------|----------------|-----------|
| **Building RAG systems** | RAGas + Promptfoo | RAGas is essential for quality metrics; Promptfoo covers RAG security gaps |
| **Security/compliance priority** | Garak + Promptfoo | Garak excels at OWASP coverage; Promptfoo adds dynamic attacks and reporting |
| **CI/CD automation critical** | Promptfoo alone | Native CI/CD design with YAML config and exit codes |
| **Python-only team** | RAGas or Garak | Both Python-native; Promptfoo requires Node.js |
| **General LLM testing** | Promptfoo alone | Covers most ground single-framework: security, comparison, quality |
| **Budget-constrained** | Start with Promptfoo | One framework covers multiple use cases; add specialists later |

### Hybrid Recommendations

| Need | Primary | Secondary |
|------|---------|------------|
| **Complete RAG testing** | RAGas (quality) | Promptfoo (security) |
| **Complete security coverage** | Garak (OWASP) | Promptfoo (dynamic attacks) |
| **Enterprise deployment** | Promptfoo (CI/CD) | Garak (compliance reports) |

---

## Quick Reference: By Category Winner

| Category | Winner | Score | Runner-Up | Score |
|----------|--------|-------|-----------|-------|
| **Security Testing** | Promptfoo | 4.67/5 | Garak | 3.67/5 |
| **OWASP Coverage** | Garak | 5/5 | Promptfoo | 4/5 |
| **Dynamic Attacks** | Promptfoo | 5/5 | Garak | 2/5 |
| **Red Teaming** | Promptfoo | 5/5 | Garak | 4/5 |
| **RAG Evaluation** | RAGas | 5/5 | Promptfoo | 2/5 |
| **Retrieval Metrics** | RAGas | 5/5 | Promptfoo | 2/5 |
| **Generation Metrics** | RAGas | 5/5 | Promptfoo | 2/5 |
| **RAG Security** | Promptfoo | 5/5 | Garak | 2/5 |
| **CI/CD Native** | Promptfoo | 5/5 | RAGas/Garak | 3/5 |
| **Provider Coverage** | Promptfoo/Garak | 5/5 | RAGas | 3/5 |
| **Observability** | Promptfoo | 4/5 | RAGas/Garak | 3/5 |
| **Usability** | RAGas | 4/5 | Promptfoo | 3.5/5 |
| **Python-Friendly** | RAGas | 4/5 | Garak | 3/5 |
| **JavaScript-Friendly** | Promptfoo | 5/5 | N/A | N/A |
