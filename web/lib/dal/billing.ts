import { createClient } from "@/lib/supabase/server";
import { cache } from "react";
import { getProfile } from "./profile";

// TODO: Replace with real Supabase table if 'usage' is not sufficient
export interface BillingStatus {
    plan: "free" | "pro" | "enterprise";
    capacity: {
        limit: number;
        used: number;
        resetDate: string;
    };
    invoices: {
        id: string;
        date: string;
        amount: number;
        status: "paid" | "pending" | "failed";
    }[];
}

/**
 * Fetches billing status. 
 * Currently derived from Profile, but ready to be hooked into 'invoices' table.
 */
export const getBillingStatus = cache(async (): Promise<BillingStatus> => {
    const profile = await getProfile();

    // Mock Invoices (Until we have a real 'invoices' table)
    // In Phase 4 we will create this table.
    const invoices = [
        { id: "inv_1", date: "2024-01-01", amount: 2000, status: "paid" as const },
        { id: "inv_2", date: "2023-12-01", amount: 2000, status: "paid" as const },
    ];

    return {
        plan: profile.tier,
        capacity: {
            limit: profile.tokens_monthly,
            used: profile.tokens_used,
            resetDate: new Date(new Date().setDate(1)).toISOString(), // 1st of next month approx
        },
        invoices,
    };
});
