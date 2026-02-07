import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function updateSession(request: NextRequest) {
    let supabaseResponse = NextResponse.next({
        request,
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
                    cookiesToSet.forEach(({ name, value, options }) => {
                        request.cookies.set(name, value)
                        supabaseResponse = NextResponse.next({
                            request,
                        })
                        supabaseResponse.cookies.set(name, value, options)
                    })
                },
            },
        }
    )

    // [PALANTIR EFFICIENCY]: Skip expensive auth check for high-frequency telemetry
    const isTelemetry = request.nextUrl.pathname.startsWith('/api/spc');
    let user = null;

    if (!isTelemetry) {
        const { data: { user: authUser } } = await supabase.auth.getUser();
        user = authUser;
    }

    if (
        !user &&
        !request.nextUrl.pathname.startsWith('/login') &&
        !request.nextUrl.pathname.startsWith('/auth') &&
        !request.nextUrl.pathname.startsWith('/pricing') &&
        !request.nextUrl.pathname.startsWith('/hud') &&
        !request.nextUrl.pathname.startsWith('/api/spc') &&
        !request.nextUrl.pathname.startsWith('/public') &&
        !request.nextUrl.pathname.startsWith('/changelog') &&
        request.nextUrl.pathname !== '/'
    ) {
        // no user, potentially respond by redirecting the user to the login page
        const url = request.nextUrl.clone()
        url.pathname = '/login'
        return NextResponse.redirect(url)
    }

    // Redirect logged-in users away from login
    if (user && request.nextUrl.pathname === '/login') {
        const dashboardUrl = request.nextUrl.clone()
        dashboardUrl.pathname = '/dashboard'
        return NextResponse.redirect(dashboardUrl)
    }

    // IMPORTANT: You *must* return the supabaseResponse object as it is. If you're
    // creating a new response object with NextResponse.next() make sure to:
    // 1. Pass the request in it, like so:
    //    const myNewResponse = NextResponse.next({ request })
    // 2. Copy over the cookies, like so:
    //    myNewResponse.cookies.setAll(supabaseResponse.cookies.getAll())
    // 3. Change the myNewResponse object to fit your needs, but avoid changing
    //    the cookies!
    return supabaseResponse
}
