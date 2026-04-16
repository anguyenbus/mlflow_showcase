# Hybrid Solutions and Multi-Framework Integration

Guide for combining Promptfoo, Garak, and RAGas to achieve comprehensive LLM evaluation coverage.

## Overview

No single framework provides complete coverage for all LLM evaluation needs. Hybrid solutions combine the strengths of multiple frameworks to achieve comprehensive security, quality, and RAG evaluation.

## Why Use Hybrid Solutions?

| Need | Single Framework Limitation | Hybrid Solution |
|------|----------------------------|-----------------|
| **RAG Systems** | RAGas lacks security, Promptfoo lacks RAG quality | RAGas + Promptfoo |
| **Security** | Garak lacks dynamic attacks, Promptfoo lacks some probes | Garak + Promptfoo |
| **Complete Coverage** | Each framework has gaps | All three frameworks |

## Hybrid Solution Patterns

### Pattern 1: Promptfoo + RAGas (RAG Systems)

**Use Case**: Comprehensive RAG system evaluation covering both quality and security.

```
┌─────────────────────────────────────────────────────────────────┐
│                    RAG SYSTEM EVALUATION                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  QUALITY EVALUATION (RAGas)          SECURITY EVALUATION        │
│  ┌──────────────────────────┐      (Promptfoo)                  │
│  │ Faithfulness             │      ┌──────────────────────────┐ │
│  │ Context Precision        │      │ Context Injection         │ │
│  │ Context Recall           │      │ Access Control Bypass     │ │
│  │ Answer Relevancy         │      │ Data Poisoning            │ │
│  └──────────────────────────┘      └──────────────────────────┘ │
│               │                               │                  │
│               └───────────────┬───────────────┘                  │
│                               ↓                                  │
│              ┌──────────────────────────────┐                   │
│              │     COMPREHENSIVE REPORT     │                   │
│              │  • Quality Metrics           │                   │
│              │  • Security Findings         │                   │
│              │  • Overall Assessment        │                   │
│              └──────────────────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation Strategy**:

1. **Quality Layer (RAGas)**
   - Run faithfulness, context precision/recall, answer relevancy
   - Measure retrieval quality
   - Track hallucination rates

2. **Security Layer (Promptfoo)**
   - Run RAG security plugin
   - Test context injection, access control, data poisoning
   - Validate guardrails

3. **Integration**
   - Run RAGas first (quality baseline)
   - Run Promptfoo security tests
   - Aggregate results in unified report

**Example Workflow**:

```bash
# Step 1: Run RAGas quality evaluation
python scripts/ragas_quality_eval.py

# Step 2: Run Promptfoo security evaluation
promptfoo eval --config rag_security.yaml

# Step 3: Aggregate results
python scripts/aggregate_rag_results.py
```

### Pattern 2: Garak + Promptfoo (Comprehensive Security)

**Use Case**: Complete security testing covering both known vulnerabilities and dynamic attacks.

```
┌─────────────────────────────────────────────────────────────────┐
│                  COMPREHENSIVE SECURITY EVALUATION             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  KNOWN VULNERABILITIES (Garak)    DYNAMIC ATTACKS (Promptfoo)   │
│  ┌──────────────────────────┐      ┌──────────────────────────┐ │
│  │ Prompt Injection (Static)│      │ Prompt Injection (Dynamic)││
│  │ DAN Jailbreaks           │      │ App-specific Jailbreaks  │ │
│  │ Encoding Attacks         │      │ Context-aware Attacks    │ │
│  │ Data Leakage             │      │ Multi-turn Attacks       │ │
│  └──────────────────────────┘      └──────────────────────────┘ │
│               │                               │                  │
│               └───────────────┬───────────────┘                  │
│                               ↓                                  │
│              ┌──────────────────────────────┐                   │
│              │     SECURITY ASSESSMENT      │                   │
│              │  • Known Vulnerabilities     │                   │
│              │  • Application-specific Risks│                   │
│              │  • OWASP Coverage           │                   │
│              └──────────────────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation Strategy**:

1. **Baseline Security (Garak)**
   - Run comprehensive probe sets
   - Establish baseline against known vulnerabilities
   - Generate OWASP coverage report

2. **Dynamic Red Teaming (Promptfoo)**
   - Generate application-specific attacks
   - Test RAG/agent security
   - Multi-turn attack scenarios

3. **Integration**
   - Run Garak for baseline (nightly)
   - Run Promptfoo for custom testing (on PR)
   - Cross-reference findings

**Example Workflow**:

```bash
# Nightly: Garak baseline
python -m garak --model_type openai --model_name gpt-4 --probes all

# On PR: Promptfoo dynamic attacks
promptfoo eval --config redteam.yaml

# Report: Cross-reference
python scripts/security_cross_reference.py
```

### Pattern 3: All Three Frameworks (Complete Coverage)

**Use Case**: Production LLM systems requiring comprehensive evaluation across all dimensions.

```
┌─────────────────────────────────────────────────────────────────┐
│              COMPREHENSIVE LLM EVALUATION SYSTEM                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  PROMPTFOO  │    │   GARAK     │    │   RAGas     │         │
│  │             │    │             │    │             │         │
│  │ • Prompt    │    │ • Security  │    │ • RAG       │         │
│  │   Testing   │    │   Baseline  │    │   Quality   │         │
│  │ • Red Team  │    │ • OWASP     │    │ • Retrieval  │         │
│  │ • RAG Sec   │    │ • Jailbreak │    │ • Faithful  │         │
│  │ • Agents    │    │ • Leakage   │    │             │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                    │                   │              │
│         └────────────────────┼───────────────────┘              │
│                              ↓                                  │
│              ┌──────────────────────────────┐                   │
│              │     UNIFIED DASHBOARD        │                   │
│              │  • Quality Metrics           │                   │
│              │  • Security Posture          │                   │
│              │  • Trend Analysis            │                   │
│              │  • Alerting                  │                   │
│              └──────────────────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation Strategy**:

1. **Define Trigger Events**
   - On PR: Quick subset from each framework
   - Nightly: Full evaluation from all frameworks
   - On Deployment: Smoke tests from each framework

2. **Data Flow Architecture**
   ```
   ┌────────┐     ┌────────┐     ┌────────┐
   │Promptoo│     │ Garak  │     │ RAGas  │
   └────┬───┘     └────┬───┘     └────┬───┘
        │              │              │
        └──────────────┼──────────────┘
                       ↓
              ┌────────────────┐
              │  Result Parser │
              └────────┬───────┘
                       ↓
              ┌────────────────┐
              │   MLflow /     │
              │   Database     │
              └────────┬───────┘
                       ↓
              ┌────────────────┐
              │  Dashboard /   │
              │  Alerts        │
              └────────────────┘
   ```

3. **Unified Reporting**
   - Aggregate metrics from all frameworks
   - Normalize scores and thresholds
   - Generate consolidated reports
   - Track trends over time

## Implementation Examples

### Example 1: RAG System Evaluation Script

```python
# scripts/comprehensive_rag_eval.py
import subprocess
import json
from pathlib import Path

def run_ragas_quality():
    """Run RAGas quality evaluation"""
    print("Running RAGas quality evaluation...")
    result = subprocess.run([
        "python", "-m", "ragas.cli",
        "--config", "ragas_config.yaml"
    ], capture_output=True, text=True)
    return json.loads(result.stdout)

def run_promptfoo_rag_security():
    """Run Promptfoo RAG security evaluation"""
    print("Running Promptfoo RAG security evaluation...")
    result = subprocess.run([
        "promptfoo", "eval",
        "--config", "rag_security.yaml",
        "--output", "rag_security_results.json"
    ], capture_output=True, text=True)
    with open("rag_security_results.json") as f:
        return json.load(f)

def aggregate_rag_results(ragas_results, promptfoo_results):
    """Aggregate results from both frameworks"""
    return {
        "quality_metrics": ragas_results,
        "security_findings": promptfoo_results,
        "overall_assessment": {
            "quality_score": ragas_results.get("faithfulness", 0),
            "security_score": promptfoo_results.get("pass_rate", 0),
            "recommendation": generate_recommendation(ragas_results, promptfoo_results)
        }
    }

def generate_recommendation(ragas_results, promptfoo_results):
    """Generate overall recommendation"""
    quality_score = ragas_results.get("faithfulness", 0)
    security_score = promptfoo_results.get("pass_rate", 0)

    if quality_score >= 0.8 and security_score >= 0.8:
        return "PRODUCTION READY"
    elif quality_score >= 0.6 and security_score >= 0.6:
        return "NEEDS IMPROVEMENT"
    else:
        return "NOT PRODUCTION READY"

if __name__ == "__main__":
    # Run evaluations
    ragas_results = run_ragas_quality()
    promptfoo_results = run_promptfoo_rag_security()

    # Aggregate results
    final_report = aggregate_rag_results(ragas_results, promptfoo_results)

    # Save report
    with open("rag_evaluation_report.json", "w") as f:
        json.dump(final_report, f, indent=2)

    print("RAG evaluation complete. Report saved to rag_evaluation_report.json")
```

### Example 2: Comprehensive Security Script

```python
# scripts/comprehensive_security_eval.py
import subprocess
import json

def run_garak_baseline():
    """Run Garak baseline security scan"""
    print("Running Garak baseline security scan...")
    subprocess.run([
        "python", "-m", "garak",
        "--model_type", "openai",
        "--model_name", "gpt-4",
        "--probes", "promptinject,dan,encoding",
        "--report_prefix", "garak_baseline"
    ])

    # Parse results
    results = []
    with open("garak_baseline.jsonl") as f:
        for line in f:
            results.append(json.loads(line))
    return results

def run_promptfoo_dynamic():
    """Run Promptfoo dynamic red teaming"""
    print("Running Promptfoo dynamic red teaming...")
    subprocess.run([
        "promptfoo", "eval",
        "--config", "redteam.yaml",
        "--output", "redteam_results.json"
    ])

    with open("redteam_results.json") as f:
        return json.load(f)

def cross_reference_findings(garak_results, promptfoo_results):
    """Cross-reference findings from both frameworks"""
    findings = {
        "garak_only": [],
        "promptfoo_only": [],
        "both_frameworks": [],
        "summary": {}
    }

    # Analyze Garak results
    for result in garak_results:
        if result.get("status") == "complete" and not result.get("passed", True):
            findings["garak_only"].append({
                "probe": result.get("probe"),
                "detector": result.get("detector"),
                "severity": "high"
            })

    # Analyze Promptfoo results
    for result in promptfoo_results.get("results", []):
        if not result.get("pass", True):
            findings["promptfoo_only"].append({
                "test": result.get("description"),
                "assertion": result.get("assertion"),
                "severity": "medium"
            })

    # Find overlaps
    garak_probes = [f["probe"] for f in findings["garak_only"]]
    promptfoo_tests = [f["test"] for f in findings["promptfoo_only"]]

    for probe in garak_probes:
        if any(probe.lower() in test.lower() for test in promptfoo_tests):
            findings["both_frameworks"].append(probe)

    findings["summary"] = {
        "total_vulnerabilities": len(findings["garak_only"]) + len(findings["promptfoo_only"]),
        "critical_findings": len(findings["both_frameworks"]),
        "framework_agreement": len(findings["both_frameworks"])
    }

    return findings

if __name__ == "__main__":
    # Run security evaluations
    garak_results = run_garak_baseline()
    promptfoo_results = run_promptfoo_dynamic()

    # Cross-reference findings
    security_report = cross_reference_findings(garak_results, promptfoo_results)

    # Save report
    with open("security_evaluation_report.json", "w") as f:
        json.dump(security_report, f, indent=2)

    print("Security evaluation complete. Report saved to security_evaluation_report.json")
```

### Example 3: Multi-Framework CI/CD Pipeline

```yaml
# .github/workflows/comprehensive-llm-eval.yml
name: Comprehensive LLM Evaluation

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Run RAGas evaluation
        run: |
          pip install ragas
          python scripts/run_ragas_eval.py
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Garak baseline
        run: |
          pip install garak
          python -m garak --model_type openai --model_name gpt-4 --probes promptinject
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Run Promptfoo red team
        run: |
          npm install -g promptfoo
          promptfoo eval --config redteam.yaml
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

  aggregate:
    needs: [quality, security]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Aggregate results
        run: |
          python scripts/aggregate_eval_results.py
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: comprehensive-evaluation-report
          path: comprehensive_report.json
```

## Data Flow and Integration

### Result Aggregation Pattern

```python
# Unified result schema
{
    "evaluation_id": "eval_20240416_123456",
    "timestamp": "2024-04-16T12:34:56Z",
    "frameworks": {
        "promptfoo": {
            "status": "passed",
            "pass_rate": 0.92,
            "total_tests": 100,
            "failed_tests": 8
        },
        "garak": {
            "status": "passed",
            "probe_pass_rate": 0.85,
            "total_probes": 50,
            "failed_probes": 7
        },
        "ragas": {
            "status": "passed",
            "faithfulness": 0.89,
            "context_precision": 0.91,
            "answer_relevancy": 0.87
        }
    },
    "overall_assessment": {
        "status": "passed",
        "quality_score": 0.89,
        "security_score": 0.88,
        "recommendation": "PRODUCTION READY"
    },
    "trends": {
        "quality_trend": "+0.02",
        "security_trend": "-0.01"
    }
}
```

### MLflow Integration Pattern

```python
# Log all framework results to MLflow
import mlflow

def log_comprehensive_results(promptfoo_results, garak_results, ragas_results):
    """Log all framework results to MLflow"""

    with mlflow.start_run():
        # Log Promptfoo results
        mlflow.log_metric("promptfoo_pass_rate", promptfoo_results["pass_rate"])
        mlflow.log_metric("promptfoo_total_tests", promptfoo_results["total_tests"])

        # Log Garak results
        mlflow.log_metric("garak_probe_pass_rate", garak_results["probe_pass_rate"])
        mlflow.log_metric("garak_total_probes", garak_results["total_probes"])

        # Log RAGas results
        mlflow.log_metric("ragas_faithfulness", ragas_results["faithfulness"])
        mlflow.log_metric("ragas_context_precision", ragas_results["context_precision"])

        # Log overall assessment
        mlflow.log_metric("overall_quality_score", calculate_overall_quality(...))
        mlflow.log_metric("overall_security_score", calculate_overall_security(...))
```

## When to Use Hybrid Solutions

| Scenario | Recommended Combination | Rationale |
|----------|------------------------|-----------|
| **RAG Systems** | RAGas + Promptfoo | Quality + security coverage |
| **Security Critical** | Garak + Promptfoo | Known + dynamic attacks |
| **Production Systems** | All three | Complete coverage |
| **Limited Resources** | Single framework | Choose based on primary need |
| **Compliance** | Garak + Promptfoo | OWASP + compliance reporting |

## Maintenance Considerations

| Aspect | Consideration |
|--------|---------------|
| **Complexity** | More frameworks = more integration work |
| **Cost** | Multiple frameworks = higher API costs |
| **Maintenance** | Need to update all frameworks |
| **Training** | Team needs expertise in multiple tools |
| **Value** | Comprehensive coverage justifies complexity |

## Related Resources

- **Framework Profiles**: Detailed profiles for [Promptfoo](../frameworks/promptfoo.md), [Garak](../frameworks/garak.md), [RAGas](../frameworks/ragas.md)
- **Configuration Examples**: [Hybrid Configuration Examples](../examples/hybrid-examples/)
- **CI/CD Integration**: [CI/CD Integration Patterns](cicd-integration.md)
- **Use Case Mapping**: [Use Case Recommendations](../comparisons/use-case-mapping.md)
