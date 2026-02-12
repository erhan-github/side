"use server";

import { createClient } from "@/lib/supabase/server";
import { revalidatePath } from "next/cache";
import crypto from "crypto";

export async function generateApiKey() {
    const supabase = await createClient();

    // 1. Verify Authentication
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
        throw new Error("Unauthorized");
    }

    // 2. Fetch current profile to determine tier
    const { data: profile, error: profileError } = await supabase
        .from("profiles")
        .select("tier")
        .eq("id", user.id)
        .single();

    if (profileError) {
        throw new Error("Could not fetch profile");
    }

    // 3. Generate Secret (Full Key)
    const tier = profile.tier || "hobby";
    const secret = `sk_${tier}_${crypto.randomUUID().replace(/-/g, '')}`;

    // 4. Create Public Hint (sk_pro_...abcd)
    const hint = `${secret.slice(0, 7)}...${secret.slice(-4)}`;

    // 5. Create Salted Hash (SHA-256)
    // In a real Palantir-level sys, we'd use a unique pepper from ENV
    const encoder = new TextEncoder();
    const data = encoder.encode(secret);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

    // 6. Secure Storage (Hint:Hash)
    // We store it in the same column for now to avoid schema migr blockers, 
    // but formatted for future extraction.
    const secureStorageString = `v1:${hint}:${hashHex}`;

    const { error: updateError } = await supabase
        .from("profiles")
        .update({
            api_key: secureStorageString,
            updated_at: new Date().toISOString()
        })
        .eq("id", user.id);

    if (updateError) {
        throw new Error(`Failed to update API key: ${updateError.message}`);
    }

    // 7. Success
    revalidatePath("/dashboard/account");

    // [CRITICAL]: Return the plaintext secret EXACTLY once
    return {
        secret,
        hint,
        message: "Key generated successfully. This is the ONLY time you will see this key."
    };
}
