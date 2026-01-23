import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
    const cookieStore = await cookies();
    const requestUrl = new URL(req.url);
    const origin = process.env.NEXT_PUBLIC_APP_URL?.trim() || requestUrl.origin;

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

    // 4. Manually apply the cookies from THAT SAME CALL to the response
    cookiesToSetDuringInitiation.forEach(({ name, value, options }) => {
        const cookieOptions = {
            ...options,
            path: '/',
            sameSite: 'lax' as const,
            secure: true,
            httpOnly: true,
        };
        console.log(`[GITHUB AUTH] Persisting verifier cookie: ${name}`);
        response.cookies.set(name, value, cookieOptions);
    });

    return response;
}
