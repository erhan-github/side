import { NextRequest, NextResponse } from "next/server";
import { supabase, isSupabaseConfigured } from "@/lib/supabase";

export async function GET(req: NextRequest) {
    const { searchParams } = new URL(req.url);
    const code = searchParams.get("code");

    if (code && isSupabaseConfigured) {
        try {
            await supabase.auth.exchangeCodeForSession(code);
        } catch (error) {
            console.error("Auth callback error:", error);
            return NextResponse.redirect(new URL("/login?error=callback_failed", req.url));
        }
    }

    return NextResponse.redirect(new URL("/dashboard", req.url));
}
