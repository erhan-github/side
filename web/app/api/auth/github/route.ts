import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
    const cookieStore = await cookies();
    const requestUrl = new URL(req.url);

    // 1. Sanitize Origin (Important for PKCE consistency)
    let origin = process.env.NEXT_PUBLIC_APP_URL?.trim() || requestUrl.origin;
    if (origin.endsWith('/')) origin = origin.slice(0, -1);

    // 2. Clear Any Conflict Cookies (Ghost State Prevention)
    cookieStore.getAll().forEach(c => {
        if (c.name.includes('auth-token') || c.name.includes('code-verifier')) {
            try { cookieStore.delete(c.name); } catch (e) { }
        }
    });

    let cookiesToSetDuringInitiation: any[] = [];

    const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                getAll() { return cookieStore.getAll() },
                setAll(toSet) {
                    toSet.forEach(c => cookiesToSetDuringInitiation.push(c));
                }
            }
        }
    );

    // 3. Single Initiation Call
    const { data, error } = await supabase.auth.signInWithOAuth({
        provider: "github",
        options: {
            redirectTo: `${origin}/api/auth/callback`,
            skipBrowserRedirect: true
        },
    });

    if (error || !data.url) {
        console.error("[GITHUB AUTH] Initiation failed:", error);
        return NextResponse.redirect(new URL("/login?error=oauth_failed", req.url));
    }

    const response = NextResponse.redirect(data.url);

    // 4. Perfect Cookie Application
    cookiesToSetDuringInitiation.forEach(({ name, value, options }) => {
        response.cookies.set(name, value, {
            ...options,
            domain: undefined, // Force domain-less for Railway
            path: '/',
            sameSite: 'lax',
            secure: true,
        });
    });

    return response;
}
