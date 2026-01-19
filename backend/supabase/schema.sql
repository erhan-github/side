-- Supabase Schema for Side
-- Run this in Supabase SQL Editor

-- Profiles table (extends auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT,
    api_key TEXT UNIQUE NOT NULL,
    tokens_monthly INTEGER DEFAULT 10000,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own profile
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

-- Policy: Service role can do anything
CREATE POLICY "Service role full access" ON public.profiles
    FOR ALL USING (auth.role() = 'service_role');

-- Index for API key lookups
CREATE INDEX IF NOT EXISTS idx_profiles_api_key ON public.profiles(api_key);

-- Function to increment tokens (atomic)
CREATE OR REPLACE FUNCTION increment_tokens(user_id UUID, amount INTEGER)
RETURNS VOID AS $$
BEGIN
    UPDATE public.profiles
    SET tokens_used = tokens_used + amount,
        updated_at = NOW()
    WHERE id = user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, api_key)
    VALUES (
        NEW.id,
        NEW.email,
        'sk_' || encode(gen_random_bytes(24), 'hex')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop existing trigger if exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Create trigger
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Comment for documentation
COMMENT ON TABLE public.profiles IS 'User profiles with API keys and token tracking. Local-first: we only store identity, never code.';
