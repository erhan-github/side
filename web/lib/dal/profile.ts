import { createClient } from "@/lib/supabase/server";
import { cache } from "react";
import { getAuthenticatedUser } from "./auth";

export interface Profile {
    id: string;
    email: string;
    api_key: string | null;
    tier: "free" | "pro" | "enterprise";
    tokens_monthly: number;
    tokens_used: number;
    created_at: string;
}

/**
 * Fetches the user's profile with strict security.
 */
export const getProfile = cache(async (): Promise<Profile> => {
    const user = await getAuthenticatedUser(); // Throws if not valid

    const supabase = await createClient();
    const { data: profile, error } = await supabase
        .from("profiles")
        .select("*")
        .eq("id", user!.id)
        .single();

    if (error) {
        throw new Error(`[DAL] Failed to fetch profile: ${error.message}`);
    }

    return profile as Profile;
});
