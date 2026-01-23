import { createServerClient } from '@supabase/ssr'
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
                            // ENFORCE Host-Only Cookies (No Domain) for Railway consistency
                            const cookieOptions = {
                                ...options,
                                domain: undefined,
                                path: '/',
                                sameSite: 'lax' as const,
                                secure: true,
                                httpOnly: options.httpOnly ?? name.includes('auth-token'),
                            };
                            console.log(`[AUTH CLIENT] Setting cookie: ${name}`);
                            cookieStore.set(name, value, cookieOptions)
                        })
                    } catch (error) {
                        // Safe to ignore in Server Components
                    }
                },
            },
        }
    )
}
