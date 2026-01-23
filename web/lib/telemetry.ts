/**
 * Sidelith Telemetry Client
 * 
 * Unified wrapper for all observability: logging, error tracking, and analytics.
 * Provides consistent interfaces for both development and production.
 */

import posthog from 'posthog-js';
import * as Sentry from '@sentry/nextjs';

// Generate a unique trace ID for this session
const TRACE_ID = typeof window !== 'undefined'
    ? crypto.randomUUID()
    : 'server-render';

/**
 * Log schema for structured events
 */
interface LogEvent {
    event: string;
    data?: Record<string, unknown>;
    level?: 'info' | 'warn' | 'error' | 'debug';
    userId?: string;
}

/**
 * Log a structured event to PostHog and console.
 */
export function logEvent(name: string, data?: Record<string, unknown>): void {
    const eventPayload = {
        app: 'sidelith',
        trace_id: TRACE_ID,
        timestamp: new Date().toISOString(),
        ...data
    };

    // Development: Console logging
    if (process.env.NODE_ENV === 'development') {
        console.log(`[TELEMETRY] ${name}`, eventPayload);
    }

    // Production: PostHog
    try {
        posthog.capture(name, eventPayload);
    } catch (e) {
        console.warn('[TELEMETRY] PostHog capture failed:', e);
    }
}

/**
 * Log an error to Sentry and PostHog.
 */
export function logError(
    error: Error | unknown,
    context?: Record<string, unknown>
): void {
    const errorPayload = {
        app: 'sidelith',
        trace_id: TRACE_ID,
        timestamp: new Date().toISOString(),
        error_name: error instanceof Error ? error.name : 'UnknownError',
        error_message: error instanceof Error ? error.message : String(error),
        ...context
    };

    // Console logging
    console.error('[TELEMETRY] Error:', error, errorPayload);

    // Sentry
    try {
        Sentry.setTag('trace_id', TRACE_ID);
        Sentry.setContext('telemetry', errorPayload);
        Sentry.captureException(error);
    } catch (e) {
        console.warn('[TELEMETRY] Sentry capture failed:', e);
    }

    // PostHog
    try {
        posthog.capture('error', errorPayload);
    } catch (e) {
        console.warn('[TELEMETRY] PostHog error capture failed:', e);
    }
}

/**
 * Inject trace ID header into fetch options.
 */
export function withTraceId(options: RequestInit = {}): RequestInit {
    return {
        ...options,
        headers: {
            ...options.headers,
            'X-Trace-ID': TRACE_ID,
        },
    };
}

/**
 * Get the current session trace ID.
 */
export function getTraceId(): string {
    return TRACE_ID;
}

/**
 * Identify the current user for telemetry.
 */
export function identifyUser(userId: string, traits?: Record<string, unknown>): void {
    try {
        posthog.identify(userId, {
            app: 'sidelith',
            ...traits
        });
        Sentry.setUser({ id: userId, ...traits });
    } catch (e) {
        console.warn('[TELEMETRY] User identification failed:', e);
    }
}

/**
 * Reset user identity (for logout).
 */
export function resetUser(): void {
    try {
        posthog.reset();
        Sentry.setUser(null);
    } catch (e) {
        console.warn('[TELEMETRY] User reset failed:', e);
    }
}
