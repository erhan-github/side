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
                        cookiesToSet.forEach(({ name, value, options }) => {
                            // Ensure robust cookie attributes for cross-origin/proxy environments
                            const cookieOptions = {
                                ...options,
                                path: options.path || '/',
                                sameSite: options.sameSite || 'lax',
                                secure: options.secure || process.env.NEXT_PUBLIC_APP_URL?.trim().startsWith('https://'),
                                httpOnly: options.httpOnly ?? name.includes('auth-token'),
                            };

                            cookieStore.set(name, value, cookieOptions)
                        })
                    } catch (error) {
                        // Logging for forensics
                        console.warn("[AUTH] Cookie Sync Warning:", error);
                    }
                },
            },
        }
    )
}
