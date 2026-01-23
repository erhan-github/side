import { createClient } from "@/lib/supabase/server";
import { cache } from "react";
import { getAuthenticatedUser } from "./auth";

export interface LedgerEntry {
    id: string;
    created_at: string;
    operation: string; // 'usage', 'refill', 'subscription_new'
    description: string;
    tokens: number; // Positive (Credit) or Negative (Usage)
    balance_after: number | null;
    status: "success" | "failed";
}

/**
 * Fetches the forensic ledger (financial history).
 */
export const getLedger = cache(async (): Promise<LedgerEntry[]> => {
    // 1. Auth Gate
    await getAuthenticatedUser();

    // 2. Fetch from 'transaction_history' table
    const supabase = await createClient();
    const { data, error } = await supabase
        .from("transaction_history")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(100);

    if (error) {
        // If table doesn't exist yet (migration pending), fall back gracefully or return empty
        console.error("[DAL] Failed to fetch ledger:", error);
        return [];
    }

    // 3. Map to interface
    return data.map((d: any) => ({
        id: d.id,
        created_at: d.created_at,
        operation: d.type,
        description: d.description || d.type,
        tokens: d.amount,
        balance_after: d.balance_after,
        status: "success",
    }));
});
