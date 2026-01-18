import { NextRequest, NextResponse } from "next/server";
import { supabase, isSupabaseConfigured } from "@/lib/supabase";

export async function GET(req: NextRequest) {
    // Check if Supabase is properly configured
    if (!isSupabaseConfigured) {
        // Redirect to dashboard for demo purposes
        return NextResponse.redirect(new URL("/dashboard?demo=true", req.url));
    }

    const { data, error } = await supabase.auth.signInWithOAuth({
        provider: "github",
        options: {
            redirectTo: `${process.env.NEXT_PUBLIC_APP_URL}/api/auth/callback`,
        },
    });

    if (error || !data.url) {
        console.error("GitHub OAuth error:", error);
        return NextResponse.redirect(new URL("/login?error=oauth_failed", req.url));
    }

    return NextResponse.redirect(data.url);
}
