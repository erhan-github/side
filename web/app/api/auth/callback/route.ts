import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextResponse, type NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
    const requestUrl = new URL(request.url)
    const code = requestUrl.searchParams.get('code')
    const next = requestUrl.searchParams.get('next') ?? '/dashboard'
    const origin = (process.env.NEXT_PUBLIC_APP_URL?.trim() || requestUrl.origin)

    // Diagnostic Logging
    const allIncomingCookies = request.cookies.getAll();
    console.log(`[AUTH CALLBACK] Incoming cookies: ${allIncomingCookies.length}`);
    allIncomingCookies.forEach(c => {
        if (c.name.includes('auth') || c.name.includes('code-verifier')) {
            console.log(`  - ${c.name}: ${c.value.substring(0, 5)}...`);
        }
    });

    if (code) {
        const cookieStore = await cookies()

        // 1. Create a dummy response to capture cookies
        let captureResponse = NextResponse.next();

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
                            cookieStore.set(name, value, options)
                        });
                        captureResponse = NextResponse.next();
                        cookiesToSet.forEach(({ name, value, options }) => {
                            captureResponse.cookies.set(name, value, options)
                        });
                    },
                },
            }
        )

        const { error } = await supabase.auth.exchangeCodeForSession(code)

        if (!error) {
            console.log('[AUTH CALLBACK] Session exchange successful');
            const redirectUrl = `${origin}${next}`;
            console.log('[AUTH CALLBACK] Redirecting to:', redirectUrl);

            // 2. Create the final redirect response
            const finalResponse = NextResponse.redirect(redirectUrl);

            // 3. Explicitly copy ALL cookies captured during the exchange
            captureResponse.cookies.getAll().forEach((cookie) => {
                console.log(`[AUTH CALLBACK] Propagating cookie to redirect: ${cookie.name}`);
                finalResponse.cookies.set(cookie.name, cookie.value);
            });

            return finalResponse;
        }

        console.error('[AUTH CALLBACK] Exchange failed:', error.message);
    }

    // Redirect to login on error
    return NextResponse.redirect(`${origin}/login?error=auth`)
}
