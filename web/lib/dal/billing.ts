import { createClient } from "@/lib/supabase/server";
import { cache } from "react";
import { getProfile } from "./profile";

// Verified: Uses 'profiles' table via getProfile() for usage tracking.
export interface BillingStatus {
    userId: string;
    plan: "free" | "pro" | "enterprise";
    capacity: {
        limit: number;
        used: number;
        resetDate: string;
    };
    portalUrl: string | null;
}

/**
 * Fetches billing status and portal URL.
 */
export const getBillingStatus = cache(async (): Promise<BillingStatus> => {
    const profile = await getProfile();

    let portalUrl = null;

    // Fetch Portal URL if customer ID exists
    if (profile.billing_customer_id && process.env.LEMONSQUEEZY_API_KEY) {
        try {
            const res = await fetch(`https://api.lemonsqueezy.com/v1/customers/${profile.billing_customer_id}`, {
                headers: {
                    Accept: "application/vnd.api+json",
                    Authorization: `Bearer ${process.env.LEMONSQUEEZY_API_KEY}`
                },
                next: { revalidate: 3600 } // Cache for 1 hour
            });

            if (res.ok) {
                const data = await res.json();
                portalUrl = data?.data?.attributes?.urls?.customer_portal || null;
            }
        } catch (e) {
            console.error("Failed to fetch LS portal URL", e);
        }
    }

    return {
        userId: profile.id,
        plan: profile.tier,
        capacity: {
            limit: profile.tokens_monthly,
            used: profile.tokens_used,
            resetDate: new Date(new Date().setDate(1)).toISOString(), // 1st of next month approx
        },
        portalUrl,
    };
});
