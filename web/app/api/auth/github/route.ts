import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET(req: NextRequest) {
    const supabase = await createClient();

    const { data, error } = await supabase.auth.signInWithOAuth({
        provider: "github",
        options: {
            redirectTo: `${process.env.NEXT_PUBLIC_APP_URL?.trim()}/api/auth/callback`,
        },
    });

    if (error || !data.url) {
        console.error("[GITHUB AUTH] OAuth initiation failed:", error);
        return NextResponse.redirect(new URL("/login?error=oauth_failed", req.url));
    }

    console.log("[GITHUB AUTH] Redirecting to GitHub OAuth");
    return NextResponse.redirect(data.url);
}
