'use client';

import { createBrowserClient } from '@supabase/ssr'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export function AuthSync() {
    const router = useRouter()
    const supabase = createBrowserClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    )

    useEffect(() => {
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
            (event, session) => {
                if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED') {
                    // Force a router refresh to sync server components with the new cookie
                    console.log('[AUTH SYNC] Syncing session to server...');
                    router.refresh();
                }
            }
        )

        return () => {
            subscription.unsubscribe()
        }
    }, [router, supabase])

    return null
}
