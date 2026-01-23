import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
    let response = NextResponse.next({
        request: {
            headers: request.headers,
        },
    })

    // Forensic Logging
    const allCookies = request.cookies.getAll();
    if (request.nextUrl.pathname.startsWith('/dashboard')) {
        console.log(`[MIDDLEWARE] Incoming cookies (${allCookies.length}): ${allCookies.map(c => c.name).join(', ')}`);
    }

    const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                getAll() {
                    return request.cookies.getAll()
                },
                setAll(cookiesToSet) {
                    // Update request
                    cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))

                    // Update response
                    response = NextResponse.next({
                        request,
                    })

                    // Inject with SameSite=None
                    cookiesToSet.forEach(({ name, value, options }) => {
                        response.cookies.set(name, value, {
                            ...options,
                            domain: undefined,
                            path: '/',
                            sameSite: 'none', // Bypass
                            secure: true,
                        })
                    })

                    // SAFETY: Re-inject ALL existing cookies as SameSite=None to prevent chunk mismatch
                    request.cookies.getAll().forEach((cookie) => {
                        if (!cookiesToSet.find(c => c.name === cookie.name)) {
                            response.cookies.set(cookie.name, cookie.value, {
                                path: '/',
                                sameSite: 'none',
                                secure: true,
                            });
                        }
                    });
                },
            },
        }
    )

    const { data: { user } } = await supabase.auth.getUser()

    if (request.nextUrl.pathname.startsWith('/dashboard')) {
        console.log(`[MIDDLEWARE] ${user ? '✅ AUTHENTICATED' : '❌ ANONYMOUS'} access to ${request.nextUrl.pathname}`);
    }

    return response
}

export const config = {
    matcher: [
        '/((?!_next/static|_next/image|favicon.ico|api/auth|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
    ],
}
