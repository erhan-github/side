import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
    const cookieStore = await cookies();
    const requestUrl = new URL(req.url);
    const origin = process.env.NEXT_PUBLIC_APP_URL?.trim() || requestUrl.origin;

    let redirectUrl = "";
    const cookiesToSetDuringInitiation: any[] = [];

    // 1. Create a specialized client to capture the single initiation call
    const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                getAll() { return cookieStore.getAll() },
                setAll(toSet) {
                    toSet.forEach(c => cookiesToSetDuringInitiation.push(c));
                    // Also update cookieStore for internal consistency
                    toSet.forEach(c => cookieStore.set(c.name, c.value, { ...c.options, path: '/' }));
                }
            }
        }
    );

    // 2. TRIGGER INITIATION EXACTLY ONCE
    const { data, error } = await supabase.auth.signInWithOAuth({
        provider: "github",
        options: {
            redirectTo: `${origin}/api/auth/callback`,
            skipBrowserRedirect: true // Get the URL so we can construct the response ourselves
        },
    });

    if (error || !data.url) {
        console.error("[GITHUB AUTH] Initiation failed:", error);
        return NextResponse.redirect(new URL("/login?error=oauth_failed", req.url));
    }

    // 3. Create the redirect response with the URL from that SINGLE initiation call
    const response = NextResponse.redirect(data.url);

    // 4. Manually apply the cookies from THAT SAME CALL to the response
    cookiesToSetDuringInitiation.forEach(({ name, value, options }) => {
        response.cookies.set(name, value, {
            ...options,
            path: '/',
            sameSite: 'lax',
            secure: true,
        });
    });

    console.log("[GITHUB AUTH] Redirecting with SINGLE-PASS synchronized cookies");
    return response;
}
