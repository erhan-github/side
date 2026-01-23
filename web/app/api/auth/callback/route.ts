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
        const redirectUrl = `${origin}${next}`;
        const response = NextResponse.redirect(redirectUrl);

        const supabase = createServerClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL!,
            process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
            {
                cookies: {
                    getAll() { return cookieStore.getAll() },
                    setAll(toSet) {
                        toSet.forEach(({ name, value, options }) => {
                            response.cookies.set(name, value, {
                                ...options,
                                path: '/',
                                sameSite: 'lax',
                                secure: true,
                            })
                        })
                    }
                }
            }
        )

        const { error } = await supabase.auth.exchangeCodeForSession(code)

        if (!error) {
            console.log('[AUTH CALLBACK] Session exchange successful.');
            return response;
        }

        console.error('[AUTH CALLBACK] Exchange failed:', error.message);
    }

    return NextResponse.redirect(`${origin}/login?error=auth`)
}
