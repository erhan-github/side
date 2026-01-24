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

        // STRATEGY: Use Client-Side Redirect (200 OK) to bypass 307 Redirect Header Limits
        // Large session cookies are often dropped on 3xx responses by proxies/LBs.
        // A 200 OK response ensures the browser accepts the Set-Cookie headers first.
        const response = new NextResponse(
            `<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=${origin}${next}" /></head><body><script>window.location.href = "${origin}${next}";</script><p>Authenticating...</p></body></html>`,
            {
                status: 200,
                headers: { 'Content-Type': 'text/html' }
            }
        );


        const supabase = createServerClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL!,
            process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
            {
                cookies: {
                    getAll() {
                        return cookieStore.getAll()
                    },
                    setAll(cookiesToSet) {
                        try {
                            console.log(`[CALLBACK] setAll called with ${cookiesToSet.length} cookies.`);
                            cookiesToSet.forEach(({ name, value, options }) => {
                                // STRATEGY: Enforce consistent cookie attributes for Railway/Prod
                                const cookieOptions = {
                                    ...options,
                                    path: '/',
                                    sameSite: 'lax' as const,
                                    secure: true,
                                };
                                console.log(`[CALLBACK] Setting cookie: ${name}, Options: ${JSON.stringify(cookieOptions)}`);
                                response.cookies.set(name, value, cookieOptions)
                            })
                        } catch (error) {
                            console.error('[CALLBACK] Error in setAll:', error);
                        }
                    },
                },
            }
        )

        const { data, error } = await supabase.auth.exchangeCodeForSession(code)

        if (!error) {
            console.log(`[AUTH CALLBACK] Exchange successful for User ID: ${data.user?.id}. Session established.`);
            return response;
        }

        console.error('[AUTH CALLBACK] Exchange error:', error.message);
    }

    return NextResponse.redirect(`${origin}/login?error=auth_callback_failed`)
}
