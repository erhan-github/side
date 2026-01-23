import { NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url)
    const code = searchParams.get('code')
    const next = searchParams.get('next') ?? '/dashboard'
    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || new URL(request.url).origin

    if (code) {
        const supabase = await createClient()
        const { error } = await supabase.auth.exchangeCodeForSession(code)

        if (!error) {
            console.log('[AUTH CALLBACK] Session exchange successful, redirecting to', next);
            // Use a manual redirect to ensure cookies are included
            return NextResponse.redirect(`${baseUrl}${next}`)
        } else {
            console.error('[AUTH CALLBACK] Session exchange failed:', error.message);
        }
    }

    // Return the user to an error page with instructions
    console.warn('[AUTH CALLBACK] No code provided or exchange failed');
    return NextResponse.redirect(`${baseUrl}/login?error=auth-code-error`)
}
