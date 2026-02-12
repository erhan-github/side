import { createClient } from "@supabase/supabase-js";

// Legacy Client for existing API routes (non-SSR)
// Supabase Configuration
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseKey || supabaseUrl.includes("placeholder")) {
    console.warn("⚠️ Supabase credentials missing or invalid. Dashboard features may be limited.");
}

export const supabase = createClient(
    supabaseUrl || "https://placeholder-project.supabase.co",
    supabaseKey || "placeholder"
);

export const isSupabaseConfigured =
    !!supabaseUrl && !supabaseUrl.includes("placeholder") && !!supabaseKey;
