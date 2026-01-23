import { NextResponse, type NextRequest } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET(request: NextRequest) {
    const requestUrl = new URL(request.url)
    const code = requestUrl.searchParams.get('code')
    const next = requestUrl.searchParams.get('next') ?? '/dashboard'
    const origin = (process.env.NEXT_PUBLIC_APP_URL?.trim() || requestUrl.origin)

    // Diagnostic Logging
    const allCookies = request.cookies.getAll();
    console.log(`[AUTH CALLBACK] Incoming cookies: ${allCookies.length}`);
    allCookies.forEach(c => {
        if (c.name.includes('auth') || c.name.includes('code-verifier')) {
            console.log(`  - ${c.name}: ${c.value.substring(0, 5)}...`);
        }
    });

    if (code) {
        const supabase = await createClient()
        const { error } = await supabase.auth.exchangeCodeForSession(code)

        if (!error) {
            console.log('[AUTH CALLBACK] Session exchange successful');
            const redirectUrl = `${origin}${next}`;
            console.log('[AUTH CALLBACK] Redirecting to:', redirectUrl);
            return NextResponse.redirect(redirectUrl);
        }

        console.error('[AUTH CALLBACK] Exchange failed:', error.message);
    }

    // Redirect to login on error
    return NextResponse.redirect(`${origin}/login?error=auth`)
}
