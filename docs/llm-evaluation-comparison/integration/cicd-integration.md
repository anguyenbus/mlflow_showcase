# CI/CD Integration Patterns

Comprehensive guide for integrating Promptfoo, Garak, and RAGas into CI/CD pipelines.

## Overview

CI/CD integration is critical for automated LLM evaluation and regression testing. This section provides patterns and examples for integrating each framework into continuous integration workflows.

## Framework CI/CD Comparison

| Capability | Promptfoo | Garak | RAGas |
|------------|-----------|-------|-------|
| **Native CI/CD Support** | Yes | CLI-based | Python scripts |
| **Exit Codes** | Proper status codes | Basic exit codes | Via Python |
| **GitHub Actions** | Native support | Via CLI | Custom workflows |
| **Output Formats** | JSON, Markdown, HTML | JSONL | JSON |
| **Configuration** | YAML (version control) | CLI + YAML | Python code |

## Promptfoo CI/CD Integration

### GitHub Actions (Native)

```yaml
# .github/workflows/llm-eval.yml
name: LLM Evaluation

on:
  pull_request:
    branches: [main]
  schedule:
    # Run nightly for full evaluation
    - cron: '0 2 * * *'
  workflow_dispatch:

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install promptfoo
        run: npm install -g promptfoo

      - name: Run LLM evaluation
        run: |
          promptfoo eval \
            --config promptfooconfig.yaml \
            --output output.json \
            --no-cache
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: evaluation-results
          path: output.json

      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('output.json', 'utf8'));
            const passRate = results.results.filter(r => r.pass).length / results.results.length * 100;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## LLM Evaluation Results\n\n**Pass Rate**: ${passRate.toFixed(1)}%\n\n[View details](https://github.com/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId})`
            });
```

### Jenkins Integration

```groovy
// Jenkinsfile
pipeline {
    agent any

    environment {
        OPENAI_API_KEY = credentials('openai-api-key')
    }

    stages {
        stage('Install') {
            steps {
                sh 'npm install -g promptfoo'
            }
        }

        stage('Evaluate') {
            steps {
                sh '''
                    promptfoo eval \
                        --config promptfooconfig.yaml \
                        --output output.json \
                        --no-cache
                '''
            }
        }

        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'output.json'
            }
        }
    }

    post {
        always {
            sh 'cat output.json | jq .results'
        }
        failure {
            mail to: 'team@example.com',
                 subject: "LLM Evaluation Failed: ${env.JOB_NAME}",
                 body: "LLM evaluation failed. Check ${env.BUILD_URL}"
        }
    }
}
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test
  - report

llm:evaluate:
  stage: test
  image: node:20
  script:
    - npm install -g promptfoo
    - promptfoo eval --config promptfooconfig.yaml --output output.json
  artifacts:
    paths:
      - output.json
    reports:
      junit: output.json
  only:
    - merge_requests
    - main

llm:nightly:
  stage: test
  image: node:20
  script:
    - npm install -g promptfoo
    - promptfoo eval --config full-config.yaml --output nightly-output.json
  artifacts:
    paths:
      - nightly-output.json
  only:
    - schedules
```

### Promptfoo CI/CD Best Practices

1. **Use environment variables** for API keys
2. **Enable caching** for faster runs (disable with `--no-cache` for testing)
3. **Run subset on PR, full on merge** for faster feedback
4. **Store results as artifacts** for trend analysis
5. **Fail builds on critical failures** using exit codes
6. **Generate compliance reports** for security testing

## Garak CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/garak-security.yml
name: LLM Security Scan

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 3 * * *'
  workflow_dispatch:

jobs:
  security-scan:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Garak
        run: |
          python -m pip install -U pip
          python -m pip install garak

      - name: Run security scan
        run: |
          python -m garak \
            --model_type openai \
            --model_name gpt-4 \
            --probes promptinject,dan,encoding \
            --report_prefix garak_scan_${{ github.run_number }}
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: garak-results
          path: garak_scan_*.jsonl

      - name: Parse results
        run: |
          python scripts/parse_garak_results.py garak_scan_*.jsonl
        continue-on-error: true
```

### Docker Compose for Garak

```yaml
# docker-compose.yml for Garak
version: '3.8'
services:
  garak:
    image: python:3.11
    command: >
      sh -c "
        pip install garak &&
        python -m garak
          --model_type openai
          --model_name ${MODEL_NAME}
          --probes ${PROBES}
          --report_prefix results
      "
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      MODEL_NAME: gpt-4
      PROBES: promptinject,dan,encoding
    volumes:
      - ./results:/app/results
```

### Garak CI/CD Best Practices

1. **Select specific probes** for faster CI runs
2. **Use report prefix** to track builds
3. **Parse JSONL output** for pass/fail determination
4. **Run nightly scans** for comprehensive coverage
5. **Monitor probe pass rates** over time
6. **Fail on critical vulnerabilities** (LLM01, LLM06)

## RAGas CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/ragas-eval.yml
name: RAG Evaluation

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 1 * * *'

jobs:
  rag-evaluate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install -U pip
          pip install ragas langchain-openai

      - name: Run RAG evaluation
        run: |
          python scripts/run_ragas_eval.py
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Upload MLflow artifacts
        uses: actions/upload-artifact@v4
        with:
          name: mlflow-artifacts
          path: mlflow-artifacts/
```

### RAGas Evaluation Script

```python
# scripts/run_ragas_eval.py
import os
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
import json

def load_test_data():
    """Load test data for RAG evaluation"""
    # Load from file or generate
    return [
        {
            "question": "What is X?",
            "answer": "X is...",
            "contexts": ["Context about X..."],
            "ground_truth": "X is..."
        }
    ]

def run_evaluation():
    """Run RAGas evaluation"""
    dataset = load_test_data()

    results = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy]
    )

    # Convert to dict for output
    results_dict = results.to_dict()

    # Save results
    with open('ragas_results.json', 'w') as f:
        json.dump(results_dict, f, indent=2)

    # Check if metrics meet threshold
    faithfulness_score = results_dict['faithfulness']
    relevancy_score = results_dict['answer_relevancy']

    if faithfulness_score < 0.8 or relevancy_score < 0.8:
        print("RAG evaluation failed: metrics below threshold")
        return 1

    return 0

if __name__ == "__main__":
    exit(run_evaluation())
```

### RAGas CI/CD Best Practices

1. **Set metric thresholds** for pass/fail determination
2. **Use subset of metrics** for faster PR checks
3. **Run full evaluation** nightly or on merge
4. **Track metric trends** over time
5. **Integrate with MLflow** for experiment tracking
6. **Generate comparison reports** for A/B testing

## MLflow Integration

### Promptfoo with MLflow

```python
# scripts/promptfoo_mlflow.py
import subprocess
import mlflow
import json
import os

def run_promptfoo_mlflow():
    """Run Promptfoo evaluation and log to MLflow"""

    with mlflow.start_run():
        # Log parameters
        mlflow.log_param("framework", "promptfoo")
        mlflow.log_param("model", "gpt-4")

        # Run Promptfoo
        result = subprocess.run(
            ["promptfoo", "eval", "--config", "promptfooconfig.yaml", "-o", "output.json"],
            capture_output=True,
            text=True
        )

        # Load and log results
        with open("output.json") as f:
            results = json.load(f)

        # Calculate metrics
        pass_count = sum(1 for r in results.get("results", []) if r.get("pass"))
        total_count = len(results.get("results", []))
        pass_rate = pass_count / total_count if total_count > 0 else 0

        # Log metrics
        mlflow.log_metric("pass_rate", pass_rate)
        mlflow.log_metric("total_tests", total_count)
        mlflow.log_metric("passed_tests", pass_count)

        # Log artifact
        mlflow.log_artifact("output.json")

        print(f"Pass rate: {pass_rate:.2%}")
        return 0 if pass_rate >= 0.8 else 1

if __name__ == "__main__":
    exit(run_promptfoo_mlflow())
```

### Garak with MLflow

```python
# scripts/garak_mlflow.py
import subprocess
import mlflow
import json

def run_garak_mlflow():
    """Run Garak scan and log to MLflow"""

    with mlflow.start_run():
        # Log parameters
        mlflow.log_param("framework", "garak")
        mlflow.log_param("probes", "promptinject,dan,encoding")

        # Run Garak
        report_prefix = "garak_scan"
        subprocess.run([
            "python", "-m", "garak",
            "--model_type", "openai",
            "--model_name", "gpt-4",
            "--probes", "promptinject,dan,encoding",
            "--report_prefix", report_prefix
        ])

        # Parse JSONL results
        results_file = f"{report_prefix}.jsonl"
        total_tests = 0
        passed_tests = 0

        with open(results_file) as f:
            for line in f:
                result = json.loads(line)
                if result.get("status") == "complete":
                    total_tests += 1
                    if result.get("passed", True):
                        passed_tests += 1

        pass_rate = passed_tests / total_tests if total_tests > 0 else 0

        # Log metrics
        mlflow.log_metric("pass_rate", pass_rate)
        mlflow.log_metric("total_tests", total_tests)
        mlflow.log_metric("passed_tests", passed_tests)

        # Log artifact
        mlflow.log_artifact(results_file)

        print(f"Security pass rate: {pass_rate:.2%}")
        return 0 if pass_rate >= 0.7 else 1

if __name__ == "__main__":
    exit(run_garak_mlflow())
```

### RAGas with MLflow

```python
# scripts/ragas_mlflow.py
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
import mlflow

def run_ragas_mlflow():
    """Run RAGas evaluation and log to MLflow"""

    with mlflow.start_run():
        # Log parameters
        mlflow.log_param("framework", "ragas")
        mlflow.log_param("metrics", "faithfulness,answer_relevancy")

        # Load test data
        dataset = load_test_data()

        # Run evaluation
        results = evaluate(
            dataset=dataset,
            metrics=[faithfulness, answer_relevancy]
        )

        # Log metrics
        results_dict = results.to_dict()
        for metric_name, metric_value in results_dict.items():
            mlflow.log_metric(metric_name, metric_value)

        print(f"Results: {results_dict}")
        return 0

if __name__ == "__main__":
    exit(run_ragas_mlflow())
```

## Multi-Framework CI/CD Pipeline

### Combined GitHub Actions Workflow

```yaml
# .github/workflows/llm-comprehensive.yml
name: Comprehensive LLM Evaluation

on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'

jobs:
  promptfoo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm install -g promptfoo
      - run: promptfoo eval --config promptfooconfig.yaml
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

  garak:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install garak
      - run: python -m garak --model_type openai --model_name gpt-4 --probes promptinject
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

  ragas:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ragas
      - run: python scripts/run_ragas_eval.py
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## CI/CD Best Practices Summary

| Practice | Promptfoo | Garak | RAGas |
|----------|-----------|-------|-------|
| **PR Checks** | Quick test subset | Critical probes only | Core metrics only |
| **Full Evaluation** | On merge to main | Nightly schedule | Nightly schedule |
| **Result Storage** | Artifacts + web UI | JSONL artifacts | MLflow logging |
| **Failure Handling** | Fail on critical | Fail on vulnerabilities | Fail on threshold |
| **Trending** | Web UI comparison | JSONL analysis | MLflow tracking |

## Related Resources

- **Framework Profiles**: Detailed profiles for [Promptfoo](../frameworks/promptfoo.md), [Garak](../frameworks/garak.md), [RAGas](../frameworks/ragas.md)
- **Technical Requirements**: [Technical Requirements](technical-requirements.md)
- **Hybrid Solutions**: [Multi-framework Integration](hybrid-solutions.md)
- **Project Tutorials**: [Promptfoo MLflow Integration](../../src/promptfoo_evaluation/), [RAGas MLflow Integration](../../src/ragas_evaluation/with_mlflows/)
