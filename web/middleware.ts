import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
    // 1. Create an initial response
    let response = NextResponse.next({
        request: {
            headers: request.headers,
        },
    })

    // [DIAGNOSTIC] Log incoming state
    const cookieNames = request.cookies.getAll().map(c => c.name).join(', ');
    console.log(`[MIDDLEWARE] INCOMING (${request.nextUrl.pathname})`);
    console.log(`[MIDDLEWARE] Cookies: [${cookieNames}]`);
    console.log(`[MIDDLEWARE] Headers: host=${request.headers.get('host')}, x-forwarded-proto=${request.headers.get('x-forwarded-proto')}, referer=${request.headers.get('referer')}`);

    const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                getAll() {
                    return request.cookies.getAll()
                },
                setAll(cookiesToSet) {
                    // Update request cookies so subsequent logic sees the new session
                    cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))

                    // Re-create response to include the new request state
                    response = NextResponse.next({
                        request,
                    })

                    // Persist cookies to the browser
                    cookiesToSet.forEach(({ name, value, options }) => {
                        // STRATEGY: Enforce consistent cookie attributes for Railway/Prod
                        const cookieOptions = {
                            ...options,
                            path: '/',
                            sameSite: 'lax' as const,
                            secure: true,
                        };
                        response.cookies.set(name, value, cookieOptions)
                    })
                },
            },
        }
    )

    // 2. Refresh session if expired
    const { data: { user }, error } = await supabase.auth.getUser()

    if (request.nextUrl.pathname.startsWith('/dashboard')) {
        console.log(`[MIDDLEWARE] Checking session for ${request.nextUrl.pathname}. User: ${user?.id || 'NONE'}. Error: ${error?.message || 'None'}`);
    }

    // 3. Protected Route Logic
    // Redirect to dashboard if logged in at root
    if (user && request.nextUrl.pathname === '/') {
        console.log(`[MIDDLEWARE] User ${user.id} at root, redirecting to /dashboard`);
        return NextResponse.redirect(new URL('/dashboard', request.url))
    }

    return response
}

export const config = {
    matcher: [
        '/((?!_next/static|_next/image|favicon.ico|api/auth|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
    ],
}
