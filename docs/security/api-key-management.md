# API Key Management and Security Practices

This document outlines security practices for managing API keys and credentials in the MLflow LLM educational repository.

## Overview

This repository uses Zhipu AI API keys for LLM model access. Proper key management is critical for:

- **Security**: Prevent unauthorized access to paid services
- **Cost control**: Avoid unexpected charges from API usage
- **Compliance**: Meet organizational security requirements
- **Development**: Enable safe local development and testing

## Authentication Requirements

### Zhipu AI API Key

- **Purpose**: Access Zhipu AI GLM-5 models (glm-5-flash, glm-5-plus, etc.)
- **Format`: `id.secret` (e.g., `1234.abcdef123456`)
- **Get key**: https://open.bigmodel.cn/
- **Permissions**: Required for all LLM operations

### Environment Variables

The following environment variables must be configured:

```bash
# Required
ZHIPU_API_KEY=your_api_key_here

# Optional
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
```

## Security Practices

### 1. Never Commit Secrets

**CRITICAL**: Never commit API keys or credentials to version control.

**❌ WRONG:**

```python
# src/config.py
API_KEY = "1234.abcdef123456"  # NEVER do this!
```

**✅ CORRECT:**

```python
# src/config.py
import os
API_KEY = os.getenv("ZHIPU_API_KEY")
```

**Git protection:**

```bash
# .gitignore
.env
.env.local
*.key
credentials.json

# Pre-commit hook to catch secrets
pre-commit run --all-files
```

### 2. Environment Variable Storage

Use `.env` files for local development (gitignored):

```bash
# .env (DO NOT COMMIT)
ZHIPU_API_KEY=1234.abcdef123456
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
```

**Provide example template:**

```bash
# .env.example (COMMIT THIS)
ZHIPU_API_KEY=your_api_key_here
MLFLOW_TRACKING_URI=sqlite:///mlflow.db
```

### 3. .gitignore Configuration

Ensure `.gitignore` prevents secret leaks:

```gitignore
# Environment files
.env
.env.local
.env.*.local

# Credentials
*.key
*.pem
credentials.json
secrets/

# MLflow artifacts (may contain sensitive data)
mlflow-artifacts/
mlflow.db
```

### 4. Validation and Error Handling

**Validate on startup:**

```python
# src/config.py
import os
from beartype import beartype

@beartype
def validate_environment() -> None:
    """Validate required environment variables are set.

    Raises:
        ValueError: If required variables are missing or empty.
    """
    api_key = os.getenv("ZHIPU_API_KEY")

    if not api_key:
        raise ValueError(
            "ZHIPU_API_KEY environment variable is required. "
            "Set it in your .env file or environment."
        )

    if not api_key.strip():
        raise ValueError(
            "ZHIPU_API_KEY cannot be empty. "
            "Please provide a valid API key."
        )

    # Basic format validation
    if "." not in api_key:
        raise ValueError(
            "ZHIPU_API_KEY format is invalid. "
            "Expected format: id.secret"
        )
```

**Handle missing keys gracefully:**

```python
try:
    validate_environment()
except ValueError as e:
    print(f"Configuration error: {e}")
    print("Please set up your .env file correctly.")
    sys.exit(1)
```

### 5. Secret Rotation

**Regular rotation schedule:**

- **Development**: Rotate every 90 days
- **Production**: Rotate every 30-60 days
- **After compromise**: Rotate immediately

**Rotation process:**

1. Generate new API key in Zhipu AI console
2. Update `.env` file with new key
3. Test with new key
4. Revoke old key in Zhipu AI console
5. Document rotation in runbook

**Key lifecycle management:**

```python
# Store key metadata (not the key itself)
KEY_METADATA = {
    "last_rotation": "2026-03-20",
    "next_rotation": "2026-06-20",
    "rotation_frequency_days": 90
}
```

### 6. Least Privilege Access

**API key permissions:**

- Use development/test keys for local development
- Use production keys only in production environments
- Set usage limits and quotas where possible
- Monitor API usage for anomalies

**Environment-specific keys:**

```bash
# Development environment
ZHIPU_API_KEY=dev_key_with_limits

# Production environment
ZHIPU_API_KEY=prod_key_with_monitoring
```

### 7. Audit and Monitoring

**Regular audits:**

- Review API key usage monthly
- Check for unexpected usage patterns
- Validate keys are still needed
- Remove unused keys

**Monitoring setup:**

```python
# Log API usage (without logging the key)
import mlflow

def log_api_usage(model: str, tokens: int) -> None:
    """Log API usage for monitoring.

    Args:
        model: Model name used.
        tokens: Number of tokens consumed.
    """
    mlflow.log_metric(f"{model}_tokens", tokens)
    mlflow.log_metric(f"{model}_api_calls", 1)
```

### 8. Secret Detection

**Use secret scanning tools:**

```bash
# Install truffleHog for secret detection
pip install truffleHog

# Scan repository for secrets
trufflehog --regex --entropy=False /path/to/repo
```

**Pre-commit hooks:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

### 9. Documentation and Training

**Document security practices:**

- Onboarding checklist for new developers
- Runbook for key rotation procedures
- Incident response plan for key compromise
- Regular security awareness training

**Example onboarding checklist:**

```markdown
## Security Setup Checklist

- [ ] Read this security guide
- [ ] Set up `.env` file from `.env.example`
- [ ] Add API key to `.env` (DO NOT COMMIT)
- [ ] Verify `.gitignore` includes `.env`
- [ ] Test configuration: `uv run python -c "from src.config import validate_environment; validate_environment()"`
- [ ] Run pre-commit hooks: `pre-commit run --all-files`
- [ ] Review incident response procedures
```

### 10. Incident Response

**If a key is compromised:**

1. **Immediate actions:**
   - Revoke the compromised key
   - Rotate to a new key
   - Review API usage logs for abuse

2. **Assessment:**
   - Determine exposure scope
   - Check for unauthorized usage
   - Assess financial impact

3. **Remediation:**
   - Rotate all related credentials
   - Audit access logs
   - Update security practices
   - Document incident

4. **Prevention:**
   - Implement additional monitoring
   - Review secret management practices
   - Update training materials

**Incident response template:**

```markdown
## Key Compromise Incident

**Date**: [DATE]
**Key**: [LAST_4_CHARS]
**Reporter**: [NAME]

### Timeline
- [TIME]: Key discovered compromised
- [TIME]: Key revoked
- [TIME]: New key issued
- [TIME]: Systems updated

### Impact
- [ ] Unauthorized usage detected
- [ ] Financial impact: $[AMOUNT]
- [ ] Data exposure: [YES/NO]

### Actions Taken
1. Revoked compromised key
2. Rotated to new key
3. Reviewed API logs
4. Updated security practices

### Prevention
- [ ] Additional monitoring implemented
- [ ] Team training completed
- [ ] Documentation updated
```

## Best Practices Summary

### DO ✅

- Use environment variables for secrets
- Provide `.env.example` templates
- Validate secrets on startup
- Rotate keys regularly
- Monitor API usage
- Use different keys for dev/prod
- Implement secret detection
- Document security practices
- Train team on security
- Have incident response plan

### DON'T ❌

- Never commit secrets to git
- Never hardcode API keys in code
- Never share keys in chat/email
- Never use production keys in development
- Never ignore security warnings
- Never skip key rotation
- Never store keys in plain text
- Never log secrets or tokens
- Never disable secret scanning
- Never assume "it won't happen to us"

## Compliance Considerations

### Organizational Policies

- Follow organizational secret management policies
- Use approved secret management systems
- Comply with data protection regulations (GDPR, CCPA)
- Adhere to industry standards (SOC 2, ISO 27001)

### Legal Requirements

- Australian Privacy Principles (if applicable)
- Data sovereignty requirements
- Audit trail for key access
- Breach notification procedures

## Tools and Resources

### Secret Management Tools

- **Local development**: `.env` files with `.gitignore`
- **Team sharing**: Password managers (1Password, Bitwarden)
- **Production**: AWS Secrets Manager, HashiCorp Vault
- **Detection**: truffleHog, detect-secrets, git-secrets

### Monitoring and Auditing

- **API usage**: Zhipu AI console
- **Cost tracking**: MLflow metrics
- **Anomaly detection**: Custom monitoring scripts
- **Audit logs**: MLflow run history

### Documentation

- Zhipu AI API documentation
- OWASP secrets management guidelines
- NIST cryptographic standards
- Industry security best practices

## Questions and Support

**Security concerns?**

- Review this document thoroughly
- Consult with security team
- Create issue in repository
- Follow incident response plan

**Need API key?**

- Visit https://open.bigmodel.cn/
- Follow Zhipu AI documentation
- Review API usage limits
- Set up billing alerts

## References

- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Zhipu AI Documentation](https://open.bigmodel.cn/dev/api)
- [MLflow Security](https://mlflow.org/docs/latest/auth/index.html)
- [Python-dotenv Documentation](https://saurabh-kumar.com/python-dotenv/)

---

**Last updated**: 2026-03-20
**Version**: 1.0
**Maintainer**: Development Team
