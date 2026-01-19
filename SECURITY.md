# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

**Email:** security@side.ai

**Please include:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes

### What to Expect

| Timeline | Action |
|----------|--------|
| 24 hours | We acknowledge receipt |
| 72 hours | We provide initial assessment |
| 7 days | We aim to have a fix in progress |
| 30 days | We aim to have released a fix |

### Safe Harbor

We will not take legal action against researchers who:
- Make a good faith effort to avoid privacy violations
- Do not access or modify other users' data
- Do not disrupt our services
- Report vulnerabilities responsibly

## Security Measures

### Data Protection

| Measure | Implementation |
|---------|----------------|
| Encryption in transit | TLS 1.3 |
| Encryption at rest | AES-256 (Supabase) |
| API authentication | Bearer tokens |
| Rate limiting | Token-based limits |

### Code Security

| Measure | Implementation |
|---------|----------------|
| Dependency scanning | Dependabot enabled |
| Secret scanning | GitHub secret scanning |
| Code review | Required for all PRs |

### Zero Retention Policy

We do not store:
- Your source code
- Your file paths
- Your git history
- Your secrets or credentials

We only store:
- Your email (for account)
- Your token usage (for billing)

## Architecture

```
User's Machine          Side API           LLM Provider
┌──────────────┐      ┌──────────┐       ┌──────────┐
│ Side MCP     │─────▶│ Stateless│──────▶│ Analysis │
│ (local)      │◀─────│ Proxy    │◀──────│          │
└──────────────┘      └──────────┘       └──────────┘
                           │
                       Zero retention.
                       Nothing stored.
```

## Compliance Roadmap

| Certification | Status | Timeline |
|--------------|--------|----------|
| GDPR | ✅ Compliant | Now |
| Privacy Policy | ✅ Complete | Now |
| SOC 2 Type I | 🎯 Planned | Post-funding |
| SOC 2 Type II | 🎯 Planned | Post-funding |
| ISO 27001 | 🎯 Planned | Post-funding |

## Contact

- **Security issues:** security@side.ai
- **General inquiries:** hello@side.ai
