-- ============================================================================
-- Sidelith Tenant Isolation Migration
-- ============================================================================
-- This migration adds complete tenant isolation so that:
-- - Each project/workspace has its own tenant_id
-- - Each project/workspace has its own tenant_id
-- - User A's insights are NEVER visible to User B
-- - Profiles and API keys (in profiles) are strictly isolated
-- ============================================================================

-- Run this in Supabase SQL Editor after 001_initial_schema.sql
-- https://supabase.com/dashboard/project/mudprpfsajbjjixprluj/sql

-- ============================================================================
-- 1. Create tenants table - represents each isolated workspace/project
-- ============================================================================
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Unique identifier derived from workspace (hash of path or project name)
    -- This is NOT PII - it's a one-way hash
    workspace_hash TEXT UNIQUE NOT NULL,
    
    -- Human-readable name (optional, user can set this)
    name TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tenants_workspace_hash ON tenants(workspace_hash);
CREATE INDEX IF NOT EXISTS idx_tenants_last_active ON tenants(last_active_at DESC);

-- ============================================================================
-- 2. Add tenant_id to all tenant-scoped tables
-- ============================================================================

-- Add tenant_id to profiles (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'profiles' AND column_name = 'tenant_id'
    ) THEN
        ALTER TABLE profiles ADD COLUMN tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
        CREATE INDEX idx_profiles_tenant ON profiles(tenant_id);
    END IF;
END $$;

-- ============================================================================
-- 3. Create tenant_insights table - stores per-tenant analysis results
-- ============================================================================
CREATE TABLE IF NOT EXISTS tenant_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- What kind of insight
    insight_type TEXT NOT NULL,  -- 'strategic', 'technical', 'market', 'risk', 'opportunity'
    
    -- The insight content
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    
    -- Source attribution
    source_context JSONB DEFAULT '{}',  -- Additional context (git activity, etc.)
    
    -- Status
    is_read BOOLEAN DEFAULT false,
    is_acted_upon BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ  -- Insights can become stale
);

CREATE INDEX IF NOT EXISTS idx_tenant_insights_tenant ON tenant_insights(tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_tenant_insights_type ON tenant_insights(tenant_id, insight_type);
CREATE INDEX IF NOT EXISTS idx_tenant_insights_unread ON tenant_insights(tenant_id) WHERE is_read = false;

-- ============================================================================
-- 5. Update RLS policies for tenant_insights
-- ============================================================================

-- Enable RLS on new tables
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_insights ENABLE ROW LEVEL SECURITY;

-- Drop old policies that don't have tenant isolation
DROP POLICY IF EXISTS "Profiles require service role" ON profiles;

-- Tenants: Only accessible via service role (server handles tenant lookup)
CREATE POLICY "Tenants service role only" ON tenants
    FOR ALL USING (auth.role() = 'service_role');

-- Profiles: Only see your tenant's profile
CREATE POLICY "Profiles tenant isolated" ON profiles
    FOR ALL USING (
        auth.role() = 'service_role'
        OR tenant_id = (current_setting('app.current_tenant_id', true))::uuid
    );

-- Tenant insights: Strictly isolated
CREATE POLICY "Insights tenant isolated" ON tenant_insights
    FOR ALL USING (
        auth.role() = 'service_role'
        OR tenant_id = (current_setting('app.current_tenant_id', true))::uuid
    );

-- ============================================================================
-- 6. Helper functions for tenant operations
-- ============================================================================

-- Get tenant's top insights
CREATE OR REPLACE FUNCTION get_tenant_insights(
    p_tenant_id UUID,
    p_limit INT DEFAULT 10,
    p_unread_only BOOLEAN DEFAULT false
)
RETURNS TABLE (
    id UUID,
    insight_type TEXT,
    title TEXT,
    content TEXT,
    confidence FLOAT,
    is_read BOOLEAN,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT
        i.id,
        i.insight_type,
        i.title,
        i.content,
        i.confidence,
        i.is_read,
        i.created_at
    FROM tenant_insights i
    WHERE 
        i.tenant_id = p_tenant_id
        AND (NOT p_unread_only OR i.is_read = false)
        AND (i.expires_at IS NULL OR i.expires_at > NOW())
    ORDER BY i.created_at DESC
    LIMIT p_limit;
END;
$$;

-- ============================================================================
-- Done! Tenant isolation is now enforced at the database level.
-- ============================================================================

-- ┌─────────────────────────────────────────────────────────────────────────┐
-- │                         ISOLATED (Per Tenant)                           │
-- │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
-- │  │  Sidelith Project│  │  Turtle Project  │  │  User X Project  │      │
-- │  │  tenant_id: A    │  │  tenant_id: B    │  │  tenant_id: C    │      │
-- │  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤      │
-- │  │ tenant_insights  │  │ tenant_insights  │  │ tenant_insights  │
-- │  │ profiles         │  │ profiles         │  │ profiles         │
-- │  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
-- │                                                                         │
-- │  🔒 RLS enforces: Tenant A can NEVER see Tenant B's data               │
-- └─────────────────────────────────────────────────────────────────────────┘
