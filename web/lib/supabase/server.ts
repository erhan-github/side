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
                            // STRIP DOMAIN to prevent Railway hosting conflicts
                            const { domain, ...otherOptions } = options;
                            const cookieOptions = {
                                ...otherOptions,
                                path: '/',
                                sameSite: 'lax' as const,
                                secure: true,
                                httpOnly: options.httpOnly ?? name.includes('auth-token'),
                            };
                            console.log(`[AUTH] Setting cookie: ${name} (httpOnly: ${cookieOptions.httpOnly})`);
                            cookieStore.set(name, value, cookieOptions)
                        })
                    } catch (error) {
                        console.warn("[AUTH] Cookie Sync Warning:", error);
                    }
                },
            },
        }
    )
}
