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
                            // STRIP DOMAIN to prevent conflicts on staging subdomains
                            const { domain, ...otherOptions } = options;
                            cookieStore.set(name, value, {
                                ...otherOptions,
                                path: '/',
                                sameSite: 'lax',
                                secure: true,
                            })
                        })
                    } catch (error) {
                        // Safe to ignore in Server Components
                    }
                },
            },
        }
    )
}
