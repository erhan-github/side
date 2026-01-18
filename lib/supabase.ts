import { createClient, SupabaseClient } from "@supabase/supabase-js";

// Fallback for build time when env vars are not set
// Using a proper URL format that Supabase SDK will accept at build time
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://placeholder-project.supabase.co";
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || "placeholder_service_role_key_that_is_at_least_40_chars_long";

export const supabase: SupabaseClient = createClient(supabaseUrl, supabaseKey, {
    auth: {
        autoRefreshToken: false,
        persistSession: false,
    },
});

// Check if we're using placeholder values (useful for runtime checks)
export const isSupabaseConfigured =
    !!process.env.NEXT_PUBLIC_SUPABASE_URL &&
    !!process.env.SUPABASE_SERVICE_ROLE_KEY &&
    !process.env.NEXT_PUBLIC_SUPABASE_URL.includes("placeholder");
