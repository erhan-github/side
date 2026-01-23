import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
    let response = NextResponse.next({
        request: {
            headers: request.headers,
        },
    })

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
                        cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
                        response = NextResponse.next({
                            request,
                        })
                        cookiesToSet.forEach(({ name, value, options }) => {
                            const { domain, ...otherOptions } = options;
                            response.cookies.set(name, value, {
                                ...otherOptions,
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

    // Forensic Logging
    const path = request.nextUrl.pathname;
    if (path.startsWith('/dashboard')) {
        console.log(`[MIDDLEWARE] ${user ? '✅ AUTHENTICATED' : '❌ ANONYMOUS'} access to ${path}`);
    }

    return response
}

export const config = {
    matcher: [
        '/((?!_next/static|_next/image|favicon.ico|api/auth|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
    ],
}
