# Privacy Policy

**Last updated:** January 2026

## One Simple Rule

> **We never see, read, or store your code.**

## Who We Are

Side AI ("Side", "we", "us") provides an AI-powered code analysis tool that runs locally on your machine. Our service is designed with privacy as the core principle.

## What We Collect

### We DO Collect

| Data | Purpose | Retention |
|------|---------|-----------|
| Email address | Account identification | Until account deletion |
| GitHub username | Account linking | Until account deletion |
| Token usage | Billing and limits | 90 days |
| Error logs | Service improvement | 30 days |

### We DO NOT Collect

| Data | Collected? |
|------|------------|
| Your source code | ❌ Never |
| Your file paths | ❌ Never |
| Your git history | ❌ Never |
| Your secrets/credentials | ❌ Never |
| Your project names | ❌ Never |

## How It Works

```
Your Machine          Side API           LLM Provider
┌──────────────┐      ┌──────────┐       ┌──────────┐
│ Side MCP     │─────▶│ Stateless│──────▶│ Analysis │
│ (reads local │◀─────│ Proxy    │◀──────│          │
│  files)      │      └──────────┘       └──────────┘
└──────────────┘           │
                       Zero retention.
                       Code passes through,
                       nothing stored.
```

1. **Side MCP** runs on your machine and reads your local files
2. **Code snippets** are sent to our API for analysis
3. **Our API** is a stateless proxy — code passes through, nothing stored
4. **Results** are returned to you
5. **Local storage** (`.side/` folder) stays on your machine

## Third-Party Services

| Service | Purpose | Their Privacy |
|---------|---------|--------------|
| Supabase | User accounts | [Supabase Privacy](https://supabase.com/privacy) |
| Groq | LLM analysis | [Groq Privacy](https://groq.com/privacy) |
| GitHub | OAuth login | [GitHub Privacy](https://docs.github.com/privacy) |

## Your Rights (GDPR)

You have the right to:
- **Access** your data
- **Correct** inaccurate data
- **Delete** your account and data
- **Export** your data
- **Object** to processing

To exercise these rights, email: privacy@side.ai

## Data Retention

| Data | Retention |
|------|-----------|
| Account data | Until you delete your account |
| Usage logs | 90 days |
| Error logs | 30 days |
| Your code | ❌ We never store it |

## Children's Privacy

Side is not intended for users under 16. We do not knowingly collect data from children.

## Changes to This Policy

We will notify you of material changes via email or in-app notification.

## Contact

- **Privacy inquiries:** privacy@side.ai
- **Data requests:** privacy@side.ai
- **General:** hello@side.ai

---

*Side AI - The Strategic Partner that thinks for you.*
