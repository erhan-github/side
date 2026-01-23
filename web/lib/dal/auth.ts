import { createClient } from "@/lib/supabase/server";
import { User } from "@supabase/supabase-js";
import { redirect } from "next/navigation";
import { cache } from "react";

/**
 * Returns the authenticated user or redirects to login.
 * This is the central gatekeeper for all Server Actions and Pages.
 * 
 * @param strict - If true (default), redirects to login if no user found.
 */
export const getAuthenticatedUser = cache(async (strict = true): Promise<User | null> => {
    const supabase = await createClient();

    const {
        data: { user },
        error
    } = await supabase.auth.getUser();

    if (error || !user) {
        if (strict) {
            redirect("/login");
        }
        return null;
    }

    return user;
});
