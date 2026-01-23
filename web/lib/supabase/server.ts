import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
    const cookieStore = await cookies()

    return createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                getAll() {
                    return cookieStore.getAll()
                },
                setAll(cookiesToSet) {
                    try {
                        cookiesToSet.forEach(({ name, value, options }) =>
                            cookieStore.set(name, value, options)
                        )
                        console.log(`[AUTH] Session Refresh: Successfully set ${cookiesToSet.length} cookies.`);
                    } catch (error) {
                        // This can consume the error if called from a Server Component
                        // but we log it for forensics in the Railway panel.
                        console.warn("[AUTH] Session Refresh Warning: Could not set cookies from Server Component.", error);
                    }
                },
            },
        }
    )
}
