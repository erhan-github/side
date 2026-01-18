"use client";

import { useEffect } from "react";
import Link from "next/link";

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        // Log error to monitoring service
        console.error("Application error:", error);
    }, [error]);

    return (
        <div className="min-h-screen bg-black text-white flex items-center justify-center px-6">
            <div className="text-center max-w-md">
                <div className="w-16 h-16 bg-red-500/20 border border-red-500/50 rounded-full flex items-center justify-center mx-auto mb-6">
                    <span className="text-3xl">⚠️</span>
                </div>
                <h1 className="text-2xl font-bold mb-2">Something went wrong</h1>
                <p className="text-zinc-400 mb-8">
                    Our strategic intelligence encountered an unexpected error.
                    We&apos;ve been notified and are looking into it.
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                    <button
                        onClick={reset}
                        className="h-12 px-8 rounded-full bg-white text-black font-semibold hover:bg-zinc-200 transition-all"
                    >
                        Try Again
                    </button>
                    <Link
                        href="/"
                        className="h-12 px-8 rounded-full border border-white/20 font-medium hover:bg-white/5 transition-all flex items-center"
                    >
                        Go Home
                    </Link>
                </div>
                {error.digest && (
                    <p className="text-xs text-zinc-600 mt-8 font-mono">
                        Error ID: {error.digest}
                    </p>
                )}
            </div>
        </div>
    );
}
