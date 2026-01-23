'use client'
import posthog from 'posthog-js'
import { PostHogProvider } from 'posthog-js/react'

if (typeof window !== 'undefined') {
    const api_key = process.env.NEXT_PUBLIC_POSTHOG_KEY;
    const host = process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com';

    if (api_key) {
        console.log("Initializing PostHog with:", host);
        posthog.init(api_key, {
            api_host: host,
            person_profiles: 'identified_only',
            capture_pageview: false
        })

        if (typeof window !== 'undefined') {
            posthog.register({
                app: 'sidelith',
                env: process.env.NODE_ENV
            })
        }
    }
}

export function CSPostHogProvider({ children }: { children: React.ReactNode }) {
    return <PostHogProvider client={posthog}>{children}</PostHogProvider>
}
