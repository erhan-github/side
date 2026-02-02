# Production Cutover Checklist (Go-Live Protocol)

This document is your **Operational Runbook** for deploying Sidelith to Staging/Production.
You are correct: **Keys must be rotated**, and **Redirect URIs must be updated**.

## 🔴 Critical Path: Auth Protocol Update

### 1. GitHub OAuth Settings
> **Why?** GitHub will block the login flow if the "Callback URL" is not explicitly whitelisted.
- [ ] Go to: **GitHub Developer Settings -> OAuth Apps -> Sidelith (Prod)**
- [ ] **Generate New Client Secret**: Rotate the key.
- [ ] **Start Transfer**: Update `SUPABASE_AUTH_EXTERNAL_GITHUB_SECRET` in Supabase with the new key.
- [ ] **Update Callback URL**:
    - **Old (Dev)**: `http://localhost:3000/api/auth/callback`
    - **New (Staging)**: `https://strong-cooperation-staging.up.railway.app/api/auth/callback`
    - **Add (Prod)**: `https://sidelith.com/api/auth/callback`

### 2. Supabase Auth Settings
> **Why?** Supabase validates the `redirectTo` parameter sent by the CLI flow.
- [ ] Go to: **Supabase Dashboard -> Authentication -> URL Configuration**
- [ ] **Site URL**: Set to your primary domain (e.g., `https://sidelith.com`).
- [ ] **Redirect URLs** (Add these explicitly):
    - `http://localhost:3000/**` (For local dev)
    - `https://strong-cooperation-staging.up.railway.app/**` (For Staging)
    - `https://sidelith.com/**` (For Prod)
    > *Note: Sidelith uses a wildcard `/**` because the CLI callback logic touches API routes.*

### 3. Environment Variables (Railway / Vercel)
> **Why?** The app needs the new keys to talk to the services.
- [ ] `NEXT_PUBLIC_SUPABASE_URL`: (Same as Dev? Or New Proj?)
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY`: (Rotated?)
- [ ] `SUPABASE_SERVICE_ROLE_KEY`: (Rotated?)
- [ ] `LEMONSQUEEZY_WEBHOOK_SECRET`: (If using a new storefront)
- [ ] `SOVEREIGN_ENV`: Set to `production` (defaults to Staging Auth Domain).

### 4. CLI Verification
Once deployed, verify the full loop with:
```bash
# 1. Login against Staging
side login

# 2. Check Profile
side mirror
# Expect: "Tier: TRIAL/PRO" (synced from DB)
```

## 🛡️ Sovereign Security Note
Do **NOT** commit `.env` files to Git.
Ensure `SOVEREIGN_ENV` is set correctly in your CI/CD pipeline.
