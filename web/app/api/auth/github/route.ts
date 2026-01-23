import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
    const cookieStore = await cookies();
    const requestUrl = new URL(req.url);
    const origin = process.env.NEXT_PUBLIC_APP_URL?.trim() || requestUrl.origin;

    let cookiesToSetDuringInitiation: any[] = [];

    // 1. Create client
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

    // 2. Trigger initiation (Single pass)
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

    // 3. NUCLEAR WIPE - Clear any ghost cookies
    cookieStore.getAll().forEach(c => {
        if (c.name.includes('auth-token') || c.name.includes('code-verifier')) {
            response.cookies.delete(c.name);
        }
    });

    // 4. Apply new verifier/cookies
    cookiesToSetDuringInitiation.forEach(({ name, value, options }) => {
        console.log(`[GITHUB AUTH] Setting initiation cookie: ${name}`);
        response.cookies.set(name, value, {
            ...options,
            domain: undefined, // Force Host-Only
            path: '/',
            sameSite: 'lax',
            secure: true,
        });
    });

    return response;
}
