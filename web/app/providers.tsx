'use client'
import posthog from 'posthog-js'
import { PostHogProvider } from 'posthog-js/react'

if (typeof window !== 'undefined') {
    const api_key = process.env.NEXT_PUBLIC_POSTHOG_KEY;
    const host = process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com';

    if (api_key) {
        try {
            console.log("Initializing PostHog with:", host);
            posthog.init(api_key, {
                api_host: host,
                person_profiles: 'identified_only',
                capture_pageview: false,
                persistence: 'localStorage',
                autocapture: false
            })

            posthog.register({
                app: 'sidelith',
                env: process.env.NODE_ENV
            })
        } catch (e) {
            console.warn("PostHog initialization failed:", e);
        }
    }
}

export function CSPostHogProvider({ children }: { children: React.ReactNode }) {
    return <PostHogProvider client={posthog}>{children}</PostHogProvider>
}
