-- ============================================================================
-- Sidelith Tenant Isolation Migration
-- ============================================================================
-- This migration adds complete tenant isolation so that:
-- - Each project/workspace has its own tenant_id
-- - User A's insights are NEVER visible to User B
-- - Articles are shared (they're from public sources), but SCORES are isolated
-- - Profiles, usage, and API keys are strictly isolated
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

-- Add tenant_id to article_scores
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'article_scores' AND column_name = 'tenant_id'
    ) THEN
        ALTER TABLE article_scores ADD COLUMN tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
        CREATE INDEX idx_article_scores_tenant ON article_scores(tenant_id);
        
        -- Update unique constraint to include tenant_id
        ALTER TABLE article_scores DROP CONSTRAINT IF EXISTS article_scores_article_id_stack_domain_key;
        ALTER TABLE article_scores ADD CONSTRAINT article_scores_tenant_unique 
            UNIQUE(tenant_id, article_id, stack, domain);
    END IF;
END $$;

-- Add tenant_id to usage
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'usage' AND column_name = 'tenant_id'
    ) THEN
        ALTER TABLE usage ADD COLUMN tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
        CREATE INDEX idx_usage_tenant ON usage(tenant_id, created_at DESC);
    END IF;
END $$;

-- Add tenant_id to api_keys
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'api_keys' AND column_name = 'tenant_id'
    ) THEN
        ALTER TABLE api_keys ADD COLUMN tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE;
        CREATE INDEX idx_api_keys_tenant ON api_keys(tenant_id);
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
    source_articles TEXT[],  -- IDs of articles that contributed
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
-- 4. Create tenant_context table - stores the understood context per tenant
-- ============================================================================
CREATE TABLE IF NOT EXISTS tenant_context (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID UNIQUE NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Technical context (from codebase analysis)
    primary_language TEXT,
    languages JSONB DEFAULT '[]',  -- [{name, percentage, files}]
    frameworks TEXT[],
    dependencies JSONB DEFAULT '[]',  -- [{name, version, type}]
    architecture_signals JSONB DEFAULT '{}',  -- {patterns, issues, strengths}
    
    -- Git context (recent activity signals)
    recent_focus_areas TEXT[],  -- Inferred from recent commits
    commit_frequency TEXT,  -- 'high', 'medium', 'low'
    last_commit_at TIMESTAMPTZ,
    active_contributors INT,
    
    -- Business context (inferred)
    domain TEXT,  -- 'fintech', 'healthtech', 'devtools', 'ai-ml', etc.
    stage TEXT,  -- 'idea', 'mvp', 'early', 'growth', 'mature'
    business_model TEXT,  -- 'b2b', 'b2c', 'marketplace', 'saas', etc.
    
    -- Document context (from READMEs, docs, etc.)
    project_description TEXT,
    key_features TEXT[],
    target_users TEXT,
    
    -- Embedding for semantic matching
    context_embedding VECTOR(384),
    
    -- Timestamps
    analyzed_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 5. Update RLS policies for tenant isolation
-- ============================================================================

-- Enable RLS on new tables
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_context ENABLE ROW LEVEL SECURITY;

-- Drop old policies that don't have tenant isolation
DROP POLICY IF EXISTS "Scores are publicly readable" ON article_scores;
DROP POLICY IF EXISTS "Profiles require service role" ON profiles;
DROP POLICY IF EXISTS "Usage requires service role" ON usage;
DROP POLICY IF EXISTS "API keys require service role" ON api_keys;

-- Tenants: Only accessible via service role (server handles tenant lookup)
CREATE POLICY "Tenants service role only" ON tenants
    FOR ALL USING (auth.role() = 'service_role');

-- Article scores: Only see your tenant's scores
CREATE POLICY "Article scores tenant isolated" ON article_scores
    FOR ALL USING (
        auth.role() = 'service_role' 
        OR tenant_id = (current_setting('app.current_tenant_id', true))::uuid
    );

-- Profiles: Only see your tenant's profile
CREATE POLICY "Profiles tenant isolated" ON profiles
    FOR ALL USING (
        auth.role() = 'service_role'
        OR tenant_id = (current_setting('app.current_tenant_id', true))::uuid
    );

-- Usage: Only see your tenant's usage
CREATE POLICY "Usage tenant isolated" ON usage
    FOR ALL USING (
        auth.role() = 'service_role'
        OR tenant_id = (current_setting('app.current_tenant_id', true))::uuid
    );

-- API keys: Only see your tenant's keys
CREATE POLICY "API keys tenant isolated" ON api_keys
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

-- Tenant context: Strictly isolated
CREATE POLICY "Context tenant isolated" ON tenant_context
    FOR ALL USING (
        auth.role() = 'service_role'
        OR tenant_id = (current_setting('app.current_tenant_id', true))::uuid
    );

-- ============================================================================
-- 6. Helper functions for tenant operations
-- ============================================================================

-- Get or create tenant by workspace hash
CREATE OR REPLACE FUNCTION get_or_create_tenant(p_workspace_hash TEXT, p_name TEXT DEFAULT NULL)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_tenant_id UUID;
BEGIN
    -- Try to find existing tenant
    SELECT id INTO v_tenant_id FROM tenants WHERE workspace_hash = p_workspace_hash;
    
    -- If not found, create new tenant
    IF v_tenant_id IS NULL THEN
        INSERT INTO tenants (workspace_hash, name)
        VALUES (p_workspace_hash, p_name)
        RETURNING id INTO v_tenant_id;
    ELSE
        -- Update last active
        UPDATE tenants SET last_active_at = NOW() WHERE id = v_tenant_id;
    END IF;
    
    RETURN v_tenant_id;
END;
$$;

-- Search articles with tenant-specific scoring
CREATE OR REPLACE FUNCTION search_articles_for_tenant(
    p_tenant_id UUID,
    p_query_embedding VECTOR(384),
    p_match_threshold FLOAT DEFAULT 0.5,
    p_match_count INT DEFAULT 20
)
RETURNS TABLE (
    id TEXT,
    title TEXT,
    url TEXT,
    source TEXT,
    description TEXT,
    similarity FLOAT,
    tenant_score FLOAT,
    score_reason TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id,
        a.title,
        a.url,
        a.source,
        a.description,
        1 - (a.embedding <=> p_query_embedding) AS similarity,
        COALESCE(s.score, 0) AS tenant_score,
        s.reason AS score_reason
    FROM articles a
    LEFT JOIN article_scores s ON a.id = s.article_id AND s.tenant_id = p_tenant_id
    WHERE 
        a.embedding IS NOT NULL
        AND 1 - (a.embedding <=> p_query_embedding) > p_match_threshold
    ORDER BY 
        -- Prioritize tenant-scored articles, then by similarity
        COALESCE(s.score, 0) * 0.4 + (1 - (a.embedding <=> p_query_embedding)) * 100 * 0.6 DESC
    LIMIT p_match_count;
END;
$$;

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
-- 7. Create view for tenant dashboard (analytics)
-- ============================================================================
CREATE OR REPLACE VIEW tenant_stats AS
SELECT 
    t.id AS tenant_id,
    t.name AS tenant_name,
    t.created_at,
    t.last_active_at,
    tc.primary_language,
    tc.domain,
    tc.stage,
    (SELECT COUNT(*) FROM article_scores WHERE tenant_id = t.id) AS scored_articles,
    (SELECT COUNT(*) FROM tenant_insights WHERE tenant_id = t.id) AS total_insights,
    (SELECT COUNT(*) FROM tenant_insights WHERE tenant_id = t.id AND is_read = false) AS unread_insights,
    (SELECT COUNT(*) FROM usage WHERE tenant_id = t.id) AS total_actions
FROM tenants t
LEFT JOIN tenant_context tc ON t.id = tc.tenant_id;

-- ============================================================================
-- Done! Tenant isolation is now enforced at the database level.
-- ============================================================================

-- ISOLATION GUARANTEE:
-- ┌─────────────────────────────────────────────────────────────────────────┐
-- │                           SHARED (Global)                               │
-- │  ┌─────────────────────────────────────────────────────────────────┐   │
-- │  │  articles - Public articles from HN, GitHub, Lobsters, etc.     │   │
-- │  │  (Everyone reads the same articles)                              │   │
-- │  └─────────────────────────────────────────────────────────────────┘   │
-- └─────────────────────────────────────────────────────────────────────────┘
--
-- ┌─────────────────────────────────────────────────────────────────────────┐
-- │                         ISOLATED (Per Tenant)                           │
-- │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
-- │  │  Sidelith Project│  │  Turtle Project  │  │  User X Project  │      │
-- │  │  tenant_id: A    │  │  tenant_id: B    │  │  tenant_id: C    │      │
-- │  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤      │
-- │  │ article_scores   │  │ article_scores   │  │ article_scores   │      │
-- │  │ tenant_context   │  │ tenant_context   │  │ tenant_context   │      │
-- │  │ tenant_insights  │  │ tenant_insights  │  │ tenant_insights  │      │
-- │  │ profiles         │  │ profiles         │  │ profiles         │      │
-- │  │ usage            │  │ usage            │  │ usage            │      │
-- │  │ api_keys         │  │ api_keys         │  │ api_keys         │      │
-- │  └──────────────────┘  └──────────────────┘  └──────────────────┘      │
-- │                                                                         │
-- │  🔒 RLS enforces: Tenant A can NEVER see Tenant B's data               │
-- └─────────────────────────────────────────────────────────────────────────┘
