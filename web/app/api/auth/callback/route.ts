import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextResponse, type NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
    const requestUrl = new URL(request.url)
    const code = requestUrl.searchParams.get('code')
    const next = requestUrl.searchParams.get('next') ?? '/dashboard'
    const origin = (process.env.NEXT_PUBLIC_APP_URL?.trim() || requestUrl.origin)

    if (code) {
        const cookieStore = await cookies()
        const redirectUrl = `${origin}${next}`;

        // 1. Create the final redirect response
        const response = NextResponse.redirect(redirectUrl);

        // 2. Create the "Response-Aware" client to set cookies on BOTH cookieStore and response
        const supabase = createServerClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL!,
            process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
            {
                cookies: {
                    getAll() {
                        return cookieStore.getAll()
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
                            cookieStore.set(name, value, cookieOptions);
                            response.cookies.set(name, value, cookieOptions);
                        });
                    },
                },
            }
        )

        const { error } = await supabase.auth.exchangeCodeForSession(code)

        if (!error) {
            console.log('[AUTH CALLBACK] Session exchange successful. Redirecting with robust cookies.');
            return response;
        }

        console.error('[AUTH CALLBACK] Exchange failed:', error.message);
    }

    // Redirect to login on error
    return NextResponse.redirect(`${origin}/login?error=auth`)
}
