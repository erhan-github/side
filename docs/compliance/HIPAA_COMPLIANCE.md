# Sidelith HIPAA Compliance Documentation

## Overview

This document outlines how Sidelith meets HIPAA (Health Insurance Portability and Accountability Act) requirements for handling Protected Health Information (PHI) in healthcare software development environments.

---

## Compliance Matrix

| HIPAA Requirement | Sidelith Implementation | Status |
|:--|:--|:--|
| Access Control (§164.312(a)) | Tier-based access + RLS | ✅ |
| Audit Controls (§164.312(b)) | ForensicStore audit logging | ✅ |
| Integrity Controls (§164.312(c)) | AES-256-GCM (Authenticated Encryption) | ✅ |
| Transmission Security (§164.312(e)) | TLS 1.3 for cloud sync | ✅ |
| Encryption (§164.312(e)(2)) | AES-256-GCM at rest | ✅ |

---

## Technical Controls

### 1. Access Control (§164.312(a)(1))

**Unique User Identification**
- Each user has unique `workspace_hash` derived from project path
- Cloud sync uses authenticated API keys per user
- Row Level Security (RLS) enforces tenant isolation

**Emergency Access Procedure**
- Admin bypass via `SUPABASE_SERVICE_KEY` for data recovery
- Audit logged when emergency access used

**Automatic Logoff**
- Token expiration enforced by Supabase JWT
- Session timeout configurable per tier

### 2. Audit Controls (§164.312(b))

**Audit Logging**
- All database access logged to `ForensicStore.audits` table
- Logged fields: timestamp, action, user_id, resource, outcome
- Retention: 7 years (configurable)

**Log Integrity**
- Audit logs encrypted with `shield.seal()`
- SHA-256 hash chain for tamper detection (future)

### 3. Integrity Controls (§164.312(c)(1))

**Data Integrity**
- All sensitive data encrypted with AES-256-GCM (Authenticated Encryption)
- Database WAL mode prevents corruption
- Atomic backups via `SovereignEngine.backup()`

**Electronic Signature**
- Decision records include `created_at` timestamp
- Future: Digital signatures for compliance-critical actions

### 4. Transmission Security (§164.312(e)(1))

**Encryption in Transit**
- Supabase connection requires TLS 1.3
- Local-only mode (airgap) available for air-gapped networks

**Network Controls**
- High Tech tier: Zero cloud sync (airgap_enabled=true)
- All external connections logged to forensic store

---

## Administrative Safeguards

### Business Associate Agreement (BAA)

Healthcare customers must execute a BAA with Sidelith before processing PHI. Contact: compliance@sidelith.com

### Workforce Training

All Sidelith employees with access to customer data complete:
- Annual HIPAA awareness training
- Security incident response training
- Access control procedure training

### Risk Assessment

Annual risk assessments performed covering:
- Technical vulnerabilities
- Administrative processes
- Physical security (for cloud infrastructure)

---

## Technical Architecture for HIPAA

```
┌──────────────────────────────────────────────────────────┐
│                   Healthcare Customer                     │
├──────────────────────────────────────────────────────────┤
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │
│  │ local.db    │   │ sovereign   │   │ .side/      │    │
│  │ (SQLCipher) │   │ .json       │   │ audit.log   │    │
│  │ AES-256     │   │ (AES-256)   │   │ (AES-256)   │    │
│  └─────────────┘   └─────────────┘   └─────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │          AIRGAP BOUNDARY (High Tech Tier)          │ │
│  │          No external network connections           │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
                          │
                          │ (Optional, disabled in airgap)
                          ▼
┌──────────────────────────────────────────────────────────┐
│                   Supabase Cloud (RLS)                   │
│  - TLS 1.3 encryption                                    │
│  - Row Level Security per workspace_hash                 │
│  - SOC 2 Type II certified infrastructure               │
└──────────────────────────────────────────────────────────┘
```

---

## Incident Response

### Breach Notification

In case of suspected PHI breach:

1. **Immediate**: Disable affected API keys
2. **Within 24h**: Notify affected customers
3. **Within 60 days**: Submit breach report to HHS (if >500 individuals)

### Contact

- Security incidents: security@sidelith.com
- Compliance questions: compliance@sidelith.com

---

## Certification Status

| Certification | Status | Target Date |
|:--|:--|:--|
| HIPAA Self-Assessment | ✅ Complete | 2026-01 |
| Third-Party HIPAA Audit | 🔄 Planned | 2026-Q3 |
| SOC 2 Type I | 🔄 Planned | 2026-Q4 |
| SOC 2 Type II | 🔄 Planned | 2027-Q1 |

---

> **Document Version**: 1.0  
> **Last Updated**: 2026-01-30  
> **Next Review**: 2026-07-30
