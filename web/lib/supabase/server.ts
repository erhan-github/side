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
                            cookieStore.set(name, value, {
                                ...options,
                                path: '/',
                                sameSite: 'lax',
                                secure: true,
                                httpOnly: options.httpOnly ?? name.includes('auth-token'),
                            })
                        })
                    } catch (error) {
                        // This can consume the error if called from a Server Component
                        console.warn("[AUTH] Cookie Sync Warning:", error);
                    }
                },
            },
        }
    )
}
