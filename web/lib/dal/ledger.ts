import { createClient } from "@/lib/supabase/server";
import { cache } from "react";
import { getAuthenticatedUser } from "./auth";

export interface LedgerEntry {
    id: string;
    created_at: string;
    operation: string; // e.g., 'inference', 'search'
    tokens: number;
    cost: number;
    status: "success" | "failed";
}

/**
 * Fetches the forensic ledger (usage history).
 */
export const getLedger = cache(async (): Promise<LedgerEntry[]> => {
    // 1. Auth Gate
    await getAuthenticatedUser();

    // 2. Fetch from 'usage' table
    const supabase = await createClient();
    const { data, error } = await supabase
        .from("usage")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(100);

    if (error) {
        console.error("[DAL] Failed to fetch ledger:", error);
        return [];
        // Or throw new Error(error.message);
    }

    // Map to interface (if table structure differs, adapt here)
    // Assuming 'usage' has: id, created_at, action (operation), tokens, cost?
    // If not, we might need to adapt.
    return data.map((d: any) => ({
        id: d.id,
        created_at: d.created_at,
        operation: d.action || "unknown",
        tokens: d.tokens || 0,
        cost: d.cost || 0,
        status: "success", // usage usually implies success unless we track failures
    }));
});
