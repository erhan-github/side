import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
    const cookieStore = await cookies();
    const requestUrl = new URL(req.url);
    const origin = process.env.NEXT_PUBLIC_APP_URL?.trim() || requestUrl.origin;

    // 1. Create a temporary client just to get the OAuth URL
    const tempClient = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        { cookies: { getAll() { return cookieStore.getAll() }, setAll() { } } }
    );

    const { data: { url: githubUrl }, error: initiationError } = await tempClient.auth.signInWithOAuth({
        provider: "github",
        options: { redirectTo: `${origin}/api/auth/callback`, skipBrowserRedirect: true },
    });

    if (initiationError || !githubUrl) {
        console.error("[GITHUB AUTH] Failed to get OAuth URL:", initiationError);
        return NextResponse.redirect(new URL("/login?error=oauth_failed", req.url));
    }

    // 2. Create the final redirect response
    const response = NextResponse.redirect(githubUrl);

    // 3. Create the "Response-Aware" client to set cookies on BOTH cookieStore and response
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
                        const cookieOptions = {
                            ...options,
                            path: '/',
                            sameSite: 'lax' as const,
                            secure: true, // Always true for GitHub OAuth on Railway
                            httpOnly: true,
                        };
                        cookieStore.set(name, value, cookieOptions);
                        response.cookies.set(name, value, cookieOptions);
                    });
                },
            },
        }
    );

    // 4. Trigger the actual OAuth initiation (which sets the code_verifier on our response)
    await supabase.auth.signInWithOAuth({
        provider: "github",
        options: { redirectTo: `${origin}/api/auth/callback` },
    });

    console.log("[GITHUB AUTH] Redirecting to GitHub with robust cookies");
    return response;
}
