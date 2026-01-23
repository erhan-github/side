import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
    let response = NextResponse.next({
        request: {
            headers: request.headers,
        },
    })

    // Forensic Logging: Audit incoming cookies
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
                    if (cookiesToSet.length > 0) {
                        // 1. Update the request headers
                        cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))

                        // 2. Refresh the response object
                        response = NextResponse.next({
                            request,
                        })

                        // 3. Apply the new cookies to the outgoing response
                        cookiesToSet.forEach(({ name, value, options }) => {
                            response.cookies.set(name, value, {
                                ...options,
                                domain: undefined, // Force Host-Only for Railway
                                path: '/',
                                sameSite: 'lax',
                                secure: true,
                            })
                        })
                    }
                },
            },
        }
    )

    const { data: { user } } = await supabase.auth.getUser()

    if (request.nextUrl.pathname.startsWith('/dashboard')) {
        console.log(`[MIDDLEWARE] ${user ? '✅ AUTHENTICATED' : '❌ ANONYMOUS'} access to ${request.nextUrl.pathname}`);
        if (user) console.log(`[MIDDLEWARE] User ID: ${user.id}`);
    }

    return response
}

export const config = {
    matcher: [
        '/((?!_next/static|_next/image|favicon.ico|api/auth|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
    ],
}
