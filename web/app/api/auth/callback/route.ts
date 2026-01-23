import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'
import { cookies } from 'next/headers'

export async function GET(request: NextRequest) {
    const requestUrl = new URL(request.url)
    const code = requestUrl.searchParams.get('code')
    const next = requestUrl.searchParams.get('next') ?? '/dashboard'
    const origin = process.env.NEXT_PUBLIC_APP_URL || requestUrl.origin

    if (code) {
        const cookieStore = await cookies()
        const supabase = createServerClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL!,
            process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
            {
                cookies: {
                    getAll() {
                        return cookieStore.getAll()
                    },
                    setAll(cookiesToSet) {
                        // Set cookies in the cookie store
                        cookiesToSet.forEach(({ name, value, options }) =>
                            cookieStore.set(name, value, options)
                        )
                    },
                },
            }
        )

        const { error } = await supabase.auth.exchangeCodeForSession(code)

        if (!error) {
            console.log('[AUTH CALLBACK] Session exchange successful');

            // Create the redirect response
            const redirectUrl = `${origin}${next}`;
            const response = NextResponse.redirect(redirectUrl);

            // CRITICAL: Manually copy all cookies from the store to the response
            // This is necessary because cookies().set() doesn't automatically
            // propagate to NextResponse.redirect() in App Router
            const allCookies = cookieStore.getAll();
            allCookies.forEach(cookie => {
                response.cookies.set(cookie.name, cookie.value, {
                    path: '/',
                    httpOnly: true,
                    sameSite: 'lax',
                    secure: true,
                });
            });

            console.log('[AUTH CALLBACK] Redirecting with', allCookies.length, 'cookies to:', redirectUrl);
            return response;
        }

        console.error('[AUTH CALLBACK] Exchange failed:', error.message);
    }

    // Redirect to login on error
    return NextResponse.redirect(`${origin}/login?error=auth`)
}
