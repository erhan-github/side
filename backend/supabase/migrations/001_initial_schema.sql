-- CSO.ai Database Schema
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/mudprpfsajbjjixprluj/sql

-- ============================================================================
-- 1. Enable pgvector extension for semantic search
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- 2. Articles table - stores all fetched articles with embeddings
-- ============================================================================
CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,  -- 'hackernews', 'lobsters', 'github', 'devto', 'arxiv'
    description TEXT,
    author TEXT,
    source_score INT,  -- HN points, GitHub stars, etc.
    
    -- Vector embedding for semantic search (384 dimensions for all-MiniLM-L6-v2)
    embedding VECTOR(384),
    
    -- Timestamps
    published_at TIMESTAMPTZ,
    fetched_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Metadata
    tags TEXT[],
    metadata JSONB DEFAULT '{}'
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_fetched_at ON articles(fetched_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_embedding ON articles USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ============================================================================
-- 3. Pre-computed scores - cache relevance scores by stack/domain
-- ============================================================================
CREATE TABLE IF NOT EXISTS article_scores (
    id SERIAL PRIMARY KEY,
    article_id TEXT REFERENCES articles(id) ON DELETE CASCADE,
    
    -- What profile this score is for
    stack TEXT NOT NULL,      -- 'python', 'typescript', 'rust', etc.
    domain TEXT NOT NULL,     -- 'ai-ml', 'fintech', 'devtools', etc.
    
    -- The score
    score FLOAT NOT NULL CHECK (score >= 0 AND score <= 100),
    reason TEXT,
    
    -- When computed
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint: one score per article per stack/domain combo
    UNIQUE(article_id, stack, domain)
);

CREATE INDEX IF NOT EXISTS idx_article_scores_lookup ON article_scores(stack, domain, score DESC);

-- ============================================================================
-- 4. Anonymous profiles - for personalization without PII
-- ============================================================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Hash of profile data (no PII stored)
    profile_hash TEXT UNIQUE NOT NULL,
    
    -- Profile data
    primary_language TEXT,
    frameworks TEXT[],
    domain TEXT,
    stage TEXT,  -- 'mvp', 'early', 'growth'
    
    -- Usage
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 5. Usage tracking - for billing and analytics
-- ============================================================================
CREATE TABLE IF NOT EXISTS usage (
    id SERIAL PRIMARY KEY,
    profile_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    
    action TEXT NOT NULL,  -- 'article_fetch', 'strategy_query', 'url_analyze', 'refresh'
    count INT DEFAULT 1,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_usage_profile ON usage(profile_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_action ON usage(action, created_at DESC);

-- ============================================================================
-- 6. API Keys - for commercial users
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- The key (hashed)
    key_hash TEXT UNIQUE NOT NULL,
    key_prefix TEXT NOT NULL,  -- First 8 chars for identification
    
    -- Owner
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    name TEXT,
    
    -- Limits
    tier TEXT DEFAULT 'free',  -- 'free', 'pro', 'team', 'enterprise'
    rate_limit_per_hour INT DEFAULT 100,
    monthly_quota INT DEFAULT 1000,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash) WHERE is_active = true;

-- ============================================================================
-- 7. Row Level Security (RLS) - secure by default
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE article_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- Articles are publicly readable (they're from public sources anyway)
CREATE POLICY "Articles are publicly readable" ON articles
    FOR SELECT USING (true);

-- Article scores are publicly readable
CREATE POLICY "Scores are publicly readable" ON article_scores
    FOR SELECT USING (true);

-- Profiles: users can only see their own (via service role for now)
CREATE POLICY "Profiles require service role" ON profiles
    FOR ALL USING (auth.role() = 'service_role');

-- Usage: service role only
CREATE POLICY "Usage requires service role" ON usage
    FOR ALL USING (auth.role() = 'service_role');

-- API Keys: service role only
CREATE POLICY "API keys require service role" ON api_keys
    FOR ALL USING (auth.role() = 'service_role');

-- ============================================================================
-- 8. Helper functions
-- ============================================================================

-- Function to search articles by semantic similarity
CREATE OR REPLACE FUNCTION search_articles(
    query_embedding VECTOR(384),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10,
    filter_source TEXT DEFAULT NULL
)
RETURNS TABLE (
    id TEXT,
    title TEXT,
    url TEXT,
    source TEXT,
    description TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id,
        a.title,
        a.url,
        a.source,
        a.description,
        1 - (a.embedding <=> query_embedding) AS similarity
    FROM articles a
    WHERE 
        a.embedding IS NOT NULL
        AND 1 - (a.embedding <=> query_embedding) > match_threshold
        AND (filter_source IS NULL OR a.source = filter_source)
    ORDER BY a.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function to get top articles for a stack/domain
CREATE OR REPLACE FUNCTION get_top_articles(
    p_stack TEXT,
    p_domain TEXT,
    p_limit INT DEFAULT 10,
    p_min_score FLOAT DEFAULT 50
)
RETURNS TABLE (
    id TEXT,
    title TEXT,
    url TEXT,
    source TEXT,
    description TEXT,
    score FLOAT,
    reason TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id,
        a.title,
        a.url,
        a.source,
        a.description,
        s.score,
        s.reason
    FROM articles a
    JOIN article_scores s ON a.id = s.article_id
    WHERE 
        s.stack = p_stack
        AND s.domain = p_domain
        AND s.score >= p_min_score
    ORDER BY s.score DESC
    LIMIT p_limit;
END;
$$;

-- ============================================================================
-- 8. CORE TABLES: PLANS, DECISIONS, LEARNINGS (Universal Sync)
-- ============================================================================

-- PLANS: Strategic roadmap items (Goals, Milestones, Tasks)
CREATE TABLE IF NOT EXISTS plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID DEFAULT gen_random_uuid(), -- Linked to a project context
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL DEFAULT 'goal', -- 'objective', 'milestone', 'goal', 'task'
    status TEXT DEFAULT 'active', -- 'active', 'done', 'dropped', 'blocked'
    due_date TIMESTAMPTZ,
    priority INT DEFAULT 0,
    parent_id UUID REFERENCES plans(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_plans_profile ON plans(profile_id);
CREATE INDEX IF NOT EXISTS idx_plans_status ON plans(status);

-- DECISIONS: Strategic choices (The "Brain")
CREATE TABLE IF NOT EXISTS decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID,
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    reasoning TEXT,
    category TEXT, -- 'tech', 'business', 'product'
    confidence INT DEFAULT 5,
    
    plan_id UUID REFERENCES plans(id),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_decisions_profile ON decisions(profile_id);

-- LEARNINGS: Insights and discoveries
CREATE TABLE IF NOT EXISTS learnings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID,
    profile_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    
    insight TEXT NOT NULL,
    source TEXT,
    impact TEXT DEFAULT 'medium',
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS for Core Tables
ALTER TABLE plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE learnings ENABLE ROW LEVEL SECURITY;

-- Only service role (server) can write for now to ensure integrity
CREATE POLICY "Plans are private" ON plans FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Decisions are private" ON decisions FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Learnings are private" ON learnings FOR ALL USING (auth.role() = 'service_role');

-- ============================================================================
-- Done! Your sideMCP database is UNIVERSAL and READY.
-- ============================================================================
