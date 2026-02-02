
import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function GET(request: Request) {
    try {
        const supabase = await createClient();

        // 1. Verify User Session
        const {
            data: { user },
            error: authError,
        } = await supabase.auth.getUser();

        if (authError || !user) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        // 2. Fetch Profile Data (Tier, Tokens)
        const { data: profile, error: dbError } = await supabase
            .from("profiles")
            .select("tier, tokens_monthly, tokens_used, email")
            .eq("id", user.id)
            .single();

        if (dbError) {
            console.error("Profile Fetch Error:", dbError);
            return NextResponse.json({ error: "Profile not found" }, { status: 404 });
        }

        // 3. Return Profile
        return NextResponse.json({
            id: user.id,
            email: profile.email || user.email,
            tier: profile.tier || "hobby",
            tokens_monthly: profile.tokens_monthly || 50,
            tokens_used: profile.tokens_used || 0,
        });

    } catch (err: any) {
        return NextResponse.json({ error: err.message }, { status: 500 });
    }
}
