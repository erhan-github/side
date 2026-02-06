import { NextResponse } from 'next/server'
// The client you created from the Server-Side Auth instructions
import { createClient } from '@/lib/supabase/server'

export async function GET(request: Request) {
    const { searchParams, origin } = new URL(request.url)
    const code = searchParams.get('code')
    // if "next" is in param, use it as the redirect URL
    const next = searchParams.get('next') ?? '/dashboard'

    // [SECURITY] Validate redirect URL to prevent open redirect attacks
    const ALLOWED_CLI_HOSTS = ['localhost', '127.0.0.1'];

    const isValidRedirect = (url: string): boolean => {
        // Internal paths are always allowed
        if (url.startsWith('/') && !url.startsWith('//')) return true;

        // External URLs must be whitelisted CLI hosts
        try {
            const parsed = new URL(url);
            return ALLOWED_CLI_HOSTS.includes(parsed.hostname);
        } catch {
            return false;
        }
    };

    if (!isValidRedirect(next)) {
        console.error(`[SECURITY] Open redirect attempt blocked: ${next}`);
        return NextResponse.redirect(`${origin}/dashboard`);
    }

    if (code) {
        const supabase = await createClient()
        const { data, error } = await supabase.auth.exchangeCodeForSession(code) // Capture data for tokens

        if (!error) {
            const forwardedHost = request.headers.get('x-forwarded-host') // original origin before load balancer
            const isLocalEnv = process.env.NODE_ENV === 'development'

            // [CLI REDIRECT LOGIC]
            // If 'next' is an absolute URL (starts with http), we assume it's a CLI/External redirect.
            // We append the tokens to the URL so the CLI can capture them.
            if (next.startsWith('http')) {
                const session = data.session;
                const redirectUrl = new URL(next);
                if (session) {
                    redirectUrl.searchParams.set('access_token', session.access_token);
                    if (session.refresh_token) {
                        redirectUrl.searchParams.set('refresh_token', session.refresh_token);
                    }
                }
                return NextResponse.redirect(redirectUrl.toString())
            }

            // Normal Dashboard Redirect
            if (isLocalEnv) {
                return NextResponse.redirect(`${origin}${next}`)
            } else if (forwardedHost) {
                return NextResponse.redirect(`https://${forwardedHost}${next}`)
            } else {
                return NextResponse.redirect(`${origin}${next}`)
            }
        }
    }

    // return the user to an error page with instructions
    return NextResponse.redirect(`${origin}/auth/auth-code-error`)
}
