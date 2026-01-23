import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
    // 1. Initialize response
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

    // 2. Create Supabase Client
    const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                getAll() {
                    return request.cookies.getAll()
                },
                setAll(cookiesToSet) {
                    // Update request headers
                    cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))

                    // RE-Initialize response to carry the new request headers forward
                    // IMPORTANT: We use the existing 'response' headers if possible, 
                    // but Next.js middleware usually requires re-creating the response
                    // to effectively pass headers to subsequent routes.
                    response = NextResponse.next({
                        request,
                    })

                    // Manually re-apply EVERY cookie to the new response to prevent chunk loss
                    // This is the absolute safest way to handle Supabase chunks in Middleware
                    request.cookies.getAll().forEach((cookie) => {
                        response.cookies.set(cookie.name, cookie.value, {
                            path: '/',
                            sameSite: 'lax',
                            secure: true,
                        });
                    });
                },
            },
        }
    )

    // 3. Verify Session
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
