import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
    const cookieStore = await cookies();
    const requestUrl = new URL(req.url);
    const origin = process.env.NEXT_PUBLIC_APP_URL?.trim() || requestUrl.origin;

    // 1. Create a dummy response to capture cookies
    let response = NextResponse.next();

    const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                getAll() {
                    return cookieStore.getAll();
                },
                setAll(cookiesToSet) {
                    cookiesToSet.forEach(({ name, value, options }) => {
                        cookieStore.set(name, value, options);
                    });
                    response = NextResponse.next();
                    cookiesToSet.forEach(({ name, value, options }) => {
                        response.cookies.set(name, value, options);
                    });
                },
            },
        }
    );

    const { data, error } = await supabase.auth.signInWithOAuth({
        provider: "github",
        options: {
            redirectTo: `${origin}/api/auth/callback`,
        },
    });

    if (error || !data.url) {
        console.error("[GITHUB AUTH] OAuth initiation failed:", error);
        return NextResponse.redirect(new URL("/login?error=oauth_failed", req.url));
    }

    console.log("[GITHUB AUTH] Redirecting to GitHub OAuth");

    // 2. Create the final redirect response
    const redirectResponse = NextResponse.redirect(data.url);

    // 3. Copy cookies from our capture response to the redirect response
    response.cookies.getAll().forEach((cookie) => {
        redirectResponse.cookies.set(cookie.name, cookie.value);
    });

    return redirectResponse;
}
