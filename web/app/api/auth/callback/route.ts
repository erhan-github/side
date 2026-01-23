import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextResponse, type NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
    const requestUrl = new URL(request.url)
    const code = requestUrl.searchParams.get('code')
    const next = requestUrl.searchParams.get('next') ?? '/dashboard'
    const origin = (process.env.NEXT_PUBLIC_APP_URL?.trim() || requestUrl.origin)

    // Forensic Audit
    const allCookies = request.cookies.getAll();
    console.log(`[AUTH CALLBACK] Incoming cookies (${allCookies.length}): ${allCookies.map(c => c.name).join(', ')}`);

    if (code) {
        const cookieStore = await cookies()
        let cookiesToSet: any[] = [];

        const supabase = createServerClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL!,
            process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
            {
                cookies: {
                    getAll() { return cookieStore.getAll() },
                    setAll(toSet) {
                        // IMPORTANT: Capture cookies during exchange call
                        toSet.forEach(c => cookiesToSet.push(c));
                    }
                }
            }
        )

        // 1. Exchange code for session (Triggers setAll)
        const { error } = await supabase.auth.exchangeCodeForSession(code)

        if (!error) {
            console.log(`[AUTH CALLBACK] Exchange successful. Preparing redirect with ${cookiesToSet.length} session cookies.`);

            // 2. Create response
            const response = NextResponse.redirect(`${origin}${next}`);

            // 3. Inject cookies with surgical precision (Naked & Secure)
            cookiesToSet.forEach(({ name, value, options }) => {
                console.log(`[AUTH CALLBACK] Injecting Session Cookie: ${name}`);
                response.cookies.set(name, value, {
                    ...options,
                    domain: undefined, // Force Host-Only
                    path: '/',
                    sameSite: 'lax',
                    secure: true,
                    httpOnly: true,
                    maxAge: options?.maxAge || 60 * 60 * 24 * 7, // Default 1 week
                });
            });

            return response;
        }

        console.error('[AUTH CALLBACK] Exchange failed:', error.message);
        return NextResponse.redirect(`${origin}/login?error=exchange_failed&msg=${encodeURIComponent(error.message)}`)
    }

    return NextResponse.redirect(`${origin}/login?error=no_code`)
}
