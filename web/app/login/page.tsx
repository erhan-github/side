"use client";

import { useState } from "react";
import Link from "next/link";
import { ChevronRight, Mail, Github, Loader2 } from "lucide-react";
import { createClient } from "@/lib/supabase/client";

export default function LoginPage() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");

    const handleGitHubLogin = async () => {
        setIsLoading(true);
        setError("");

        try {
            // [Check for CLI Redirect]
            const params = new URLSearchParams(window.location.search);
            const cliRedirect = params.get("cli_redirect");

            const supabase = createClient();

            // If CLI redirect exists, we append it to the callback URL
            let redirectUrl = `${window.location.origin}/api/auth/callback`;
            if (cliRedirect) {
                redirectUrl += `?next=${encodeURIComponent(cliRedirect)}`;
            } else {
                redirectUrl += `?next=/dashboard`;
            }

            const { error } = await supabase.auth.signInWithOAuth({
                provider: "github",
                options: {
                    redirectTo: redirectUrl,
                },
            });

            if (error) {
                console.error("GitHub Login Error:", error);
                setError(error.message);
                setIsLoading(false);
            }
            // If success, Supabase will redirect us away.
        } catch (err) {
            console.error("Login Exception:", err);
            setError("Something went wrong initiating login.");
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-black text-white flex items-center justify-center px-6">
            <div className="max-w-md w-full">
                {/* Logo */}
                <Link href="/" className="flex items-center gap-2 justify-center mb-12">
                    <div className="h-8 w-8 bg-white rounded-sm" />
                    <span className="font-bold text-2xl tracking-tighter uppercase italic">Side<span className="not-italic lowercase font-light text-zinc-500">lith</span></span>
                </Link>

                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold mb-2 tracking-tight">Welcome to Sidelith</h1>
                    <p className="text-zinc-400">
                        The Intelligence Infrastructure for your Codebase
                    </p>
                </div>

                {/* GitHub Button */}
                <button
                    onClick={handleGitHubLogin}
                    disabled={isLoading}
                    className="w-full h-12 rounded-full bg-zinc-900 border border-white/10 flex items-center justify-center gap-3 font-bold uppercase tracking-widest text-[11px] hover:bg-zinc-800 transition-all mb-6 disabled:opacity-50"
                >
                    {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Github className="w-5 h-5" />}
                    Authorize with GitHub
                </button>

                {error && (
                    <p className="text-red-400 text-sm mb-4 text-center">{error}</p>
                )}

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
