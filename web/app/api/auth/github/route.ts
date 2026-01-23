import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
    const cookieStore = await cookies();
    const requestUrl = new URL(req.url);
    const origin = process.env.NEXT_PUBLIC_APP_URL?.trim() || requestUrl.origin;

    // 1. Create a dummy client just to get the OAuth URL
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

    // 3. Create a production-ready client that writes directly to the redirection response
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
                            secure: true,
                            httpOnly: true,
                        };
                        // Note: We only set on response because NextResponse.redirect is a clean slate
                        response.cookies.set(name, value, cookieOptions);
                    });
                },
            },
        }
    );

    // 4. Trigger the actual OAuth initiation to generate and save the PKCE verifier
    await supabase.auth.signInWithOAuth({
        provider: "github",
        options: { redirectTo: `${origin}/api/auth/callback` },
    });

    console.log("[GITHUB AUTH] Redirecting to GitHub with Palantir-level cookie security");
    return response;
}
