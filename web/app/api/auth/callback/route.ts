import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { NextResponse, type NextRequest } from 'next/server'

export async function GET(request: NextRequest) {
    const requestUrl = new URL(request.url)
    const code = requestUrl.searchParams.get('code')
    const next = requestUrl.searchParams.get('next') ?? '/dashboard'
    const origin = (process.env.NEXT_PUBLIC_APP_URL?.trim() || requestUrl.origin)

    if (code) {
        const cookieStore = await cookies()
        const response = NextResponse.redirect(`${origin}${next}`);

        const supabase = createServerClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL!,
            process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
            {
                cookies: {
                    getAll() { return cookieStore.getAll() },
                    setAll(toSet) {
                        toSet.forEach(({ name, value, options }) => {
                            console.log(`[AUTH CALLBACK] Setting SameSite=None cookie: ${name}`);
                            const settings = {
                                ...options,
                                domain: undefined,
                                path: '/',
                                sameSite: 'none' as const, // CRITICAL
                                secure: true,
                            };

                            // Dual Injection
                            cookieStore.set(name, value, settings);
                            response.cookies.set(name, value, settings);
                        })
                    }
                }
            }
        )

        const { error } = await supabase.auth.exchangeCodeForSession(code)

        if (!error) {
            console.log('[AUTH CALLBACK] Exchange successful.');
            return response;
        }

        console.error('[AUTH CALLBACK] Exchange error:', error.message);
    }

    return NextResponse.redirect(`${origin}/login?error=auth_callback_failed`)
}
