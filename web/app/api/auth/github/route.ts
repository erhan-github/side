import { NextRequest, NextResponse } from "next/server";
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

export async function GET(req: NextRequest) {
    const cookieStore = await cookies();

    const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                getAll() {
                    return cookieStore.getAll();
                },
                setAll(cookiesToSet) {
                    cookiesToSet.forEach(({ name, value, options }) =>
                        cookieStore.set(name, value, {
                            ...options,
                            domain: new URL(process.env.NEXT_PUBLIC_APP_URL!).hostname,
                            sameSite: 'lax',
                            secure: process.env.NODE_ENV === 'production',
                            path: '/',
                        })
                    );
                },
            },
        }
    );

    const { data, error } = await supabase.auth.signInWithOAuth({
        provider: "github",
        options: {
            redirectTo: `${process.env.NEXT_PUBLIC_APP_URL}/api/auth/callback`,
        },
    });

    if (error || !data.url) {
        console.error("[GITHUB AUTH] OAuth initiation failed:", error);
        return NextResponse.redirect(new URL("/login?error=oauth_failed", req.url));
    }

    console.log("[GITHUB AUTH] Redirecting to GitHub OAuth");
    return NextResponse.redirect(data.url);
}
