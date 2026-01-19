"use client";

import { useState } from "react";
import Link from "next/link";
import { ChevronRight, Mail, Github, Loader2 } from "lucide-react";

export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [isSent, setIsSent] = useState(false);
    const [error, setError] = useState("");

    const handleMagicLink = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError("");

        try {
            // This will be connected to Supabase Auth
            const response = await fetch("/api/auth/magic-link", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email }),
            });

            if (!response.ok) {
                throw new Error("Failed to send magic link");
            }

            setIsSent(true);
        } catch {
            setError("Something went wrong. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleGitHubLogin = () => {
        // Will redirect to Supabase GitHub OAuth
        window.location.href = "/api/auth/github";
    };

    if (isSent) {
        return (
            <div className="min-h-screen bg-black text-white flex items-center justify-center px-6">
                <div className="max-w-md w-full text-center">
                    <div className="w-16 h-16 bg-green-500/20 border border-green-500/50 rounded-full flex items-center justify-center mx-auto mb-6">
                        <Mail className="w-8 h-8 text-green-400" />
                    </div>
                    <h1 className="text-2xl font-bold mb-4">Check your email</h1>
                    <p className="text-zinc-400 mb-8">
                        We sent a magic link to <strong className="text-white">{email}</strong>.
                        Click it to sign in.
                    </p>
                    <button
                        onClick={() => setIsSent(false)}
                        className="text-zinc-400 hover:text-white transition-colors"
                    >
                        Use a different email
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-black text-white flex items-center justify-center px-6">
            <div className="max-w-md w-full">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-2 justify-center mb-12">
                    <div className="h-8 w-8 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-sm" />
                    <span className="font-bold text-xl tracking-tight">Side</span>
                </Link>

                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold mb-2">Welcome to Side</h1>
                    <p className="text-zinc-400">
                        The Strategic Partner that thinks for you
                    </p>
                </div>

                {/* GitHub Button */}
                <button
                    onClick={handleGitHubLogin}
                    className="w-full h-12 rounded-full bg-zinc-900 border border-white/10 flex items-center justify-center gap-3 font-medium hover:bg-zinc-800 transition-all mb-6"
                >
                    <Github className="w-5 h-5" />
                    Continue with GitHub
                </button>

                {/* Divider */}
                <div className="flex items-center gap-4 mb-6">
                    <div className="flex-1 h-px bg-white/10" />
                    <span className="text-xs text-zinc-500 uppercase">or</span>
                    <div className="flex-1 h-px bg-white/10" />
                </div>

                {/* Email Form */}
                <form onSubmit={handleMagicLink}>
                    <div className="mb-4">
                        <label htmlFor="email" className="block text-sm font-medium text-zinc-400 mb-2">
                            Email address
                        </label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="you@company.com"
                            required
                            className="w-full h-12 px-4 rounded-lg bg-zinc-900 border border-white/10 text-white placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-white/20 transition-all"
                        />
                    </div>

                    {error && (
                        <p className="text-red-400 text-sm mb-4">{error}</p>
                    )}

                    <button
                        type="submit"
                        disabled={isLoading || !email}
                        className="w-full h-12 rounded-full bg-white text-black font-semibold flex items-center justify-center gap-2 hover:bg-zinc-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <>
                                Send Magic Link <ChevronRight className="w-4 h-4" />
                            </>
                        )}
                    </button>
                </form>

                {/* Footer */}
                <p className="text-center text-xs text-zinc-500 mt-8">
                    By continuing, you agree to our{" "}
                    <Link href="/terms" className="text-zinc-400 hover:text-white">Terms of Service</Link>
                    {" "}and{" "}
                    <Link href="/privacy" className="text-zinc-400 hover:text-white">Privacy Policy</Link>.
                </p>
            </div>
        </div>
    );
}
