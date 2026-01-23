"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import * as Sentry from "@sentry/nextjs";
import { logError, getTraceId } from "@/lib/telemetry";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

/**
 * Global Error Boundary for React application.
 * 
 * Catches all React errors and:
 * - Reports to Sentry with session replay link
 * - Logs to PostHog for analytics
 * - Renders a fallback UI with recovery options
 */
export class GlobalErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error: Error): Partial<State> {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
        this.setState({ errorInfo });

        // Report to telemetry
        logError(error, {
            componentStack: errorInfo.componentStack,
            boundary: "GlobalErrorBoundary",
        });

        // Sentry with additional context
        Sentry.withScope((scope) => {
            scope.setTag("trace_id", getTraceId());
            scope.setContext("react", {
                componentStack: errorInfo.componentStack,
            });
            Sentry.captureException(error);
        });
    }

    handleReload = (): void => {
        window.location.reload();
    };

    handleReportIssue = (): void => {
        // Open Sentry feedback dialog if available
        if (typeof Sentry.showReportDialog === "function") {
            Sentry.showReportDialog();
        }
    };

    render(): ReactNode {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="min-h-screen bg-black flex items-center justify-center p-8">
                    <div className="max-w-md w-full bg-zinc-900 border border-red-500/20 rounded-xl p-8 text-center">
                        <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
                            <AlertTriangle className="w-8 h-8 text-red-500" />
                        </div>

                        <h1 className="text-2xl font-bold text-white mb-2">
                            Something went wrong
                        </h1>

                        <p className="text-zinc-400 mb-6 text-sm">
                            An unexpected error occurred. Our team has been notified and is investigating.
                        </p>

                        <div className="bg-zinc-800 rounded-lg p-4 mb-6 text-left">
                            <p className="text-xs text-zinc-500 mb-1 font-mono uppercase tracking-wider">
                                Error Details
                            </p>
                            <p className="text-sm text-red-400 font-mono break-all">
                                {this.state.error?.message || "Unknown error"}
                            </p>
                            <p className="text-xs text-zinc-600 font-mono mt-2">
                                Trace ID: {getTraceId().slice(0, 8)}...
                            </p>
                        </div>

                        <div className="flex gap-3">
                            <button
                                onClick={this.handleReload}
                                className="flex-1 bg-white text-black hover:bg-zinc-200 py-3 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors"
                            >
                                <RefreshCw className="w-4 h-4" />
                                Reload Page
                            </button>
                            <button
                                onClick={this.handleReportIssue}
                                className="flex-1 bg-zinc-800 text-white hover:bg-zinc-700 py-3 rounded-lg font-medium transition-colors border border-zinc-700"
                            >
                                Report Issue
                            </button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default GlobalErrorBoundary;
