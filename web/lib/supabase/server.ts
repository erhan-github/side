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
                            // STRATEGY: SameSite=None (Bypass Public Suffix Restrictions)
                            const cookieOptions = {
                                ...options,
                                domain: undefined,
                                path: '/',
                                sameSite: 'none' as const, // CRITICAL CHANGE
                                secure: true,
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
