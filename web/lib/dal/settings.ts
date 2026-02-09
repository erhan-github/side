import { createClient } from "@/lib/supabase/server";
import { cache } from "react";
import { getProfile } from "./profile";
import { getAuthenticatedUser } from "./auth";

export interface Settings {
    ghost_mode: boolean;
    data_region: "eu" | "us";
}

/**
 * Fetches user settings.
 * Currently defaults to standard values until 'settings' table is live.
 */
export const getSettings = cache(async (): Promise<Settings> => {
    // Ensure auth
    await getAuthenticatedUser();

    // NOTE: 'user_settings' table pending. Using defaults for Production V1.
    return {
        ghost_mode: false,
        data_region: "eu",
    };
});
