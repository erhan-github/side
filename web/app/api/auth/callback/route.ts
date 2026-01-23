import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'
import { cookies } from 'next/headers'
import type { CookieOptions } from '@supabase/ssr'

export async function GET(request: NextRequest) {
    const requestUrl = new URL(request.url)
    const code = requestUrl.searchParams.get('code')
    const next = requestUrl.searchParams.get('next') ?? '/dashboard'
    const origin = process.env.NEXT_PUBLIC_APP_URL || requestUrl.origin

    if (code) {
        const cookieStore = await cookies()

        // Track cookies that Supabase sets during the exchange
        const cookiesToSet: Array<{ name: string; value: string; options: CookieOptions }> = []

        const supabase = createServerClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL!,
            process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
            {
                cookies: {
                    getAll() {
                        return cookieStore.getAll()
                    },
                    setAll(newCookies) {
                        // Capture the cookies Supabase wants to set
                        cookiesToSet.push(...newCookies)
                        // Also set them in the cookie store
                        newCookies.forEach(({ name, value, options }) =>
                            cookieStore.set(name, value, options)
                        )
                    },
                },
            }
        )

        const { error } = await supabase.auth.exchangeCodeForSession(code)

        if (!error) {
            console.log('[AUTH CALLBACK] Session exchange successful');
            console.log('[AUTH CALLBACK] Supabase set', cookiesToSet.length, 'cookies');

            // Create the redirect response
            const redirectUrl = `${origin}${next}`;
            const response = NextResponse.redirect(redirectUrl);

            // Copy the cookies that Supabase set to the response
            cookiesToSet.forEach(({ name, value, options }) => {
                response.cookies.set(name, value, {
                    ...options,
                    secure: process.env.NODE_ENV === 'production',
                });
            });

            console.log('[AUTH CALLBACK] Redirecting to:', redirectUrl);
            return response;
        }

        console.error('[AUTH CALLBACK] Exchange failed:', error.message);
    }

    // Redirect to login on error
    return NextResponse.redirect(`${origin}/login?error=auth`)
}
