"use client";

import { useState } from "react";
import Link from "next/link";
import { Github, Loader2 } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { BrandLogo } from "@/components/ui/BrandLogo";

export default function LoginPage() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");

    const handleGitHubLogin = async () => {
        setIsLoading(true);
        setError("");

        try {
            const params = new URLSearchParams(window.location.search);
            const cliRedirect = params.get("cli_redirect");
            const supabase = createClient();

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
        } catch (err) {
            console.error("Login Exception:", err);
            setError("Something went wrong. Please try again.");
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-black text-white flex items-center justify-center px-6">
            <div className="max-w-md w-full">
                {/* Logo */}
                <div className="flex justify-center mb-12">
                    <BrandLogo size="lg" />
                </div>

                {/* Header - FIXED: Removed jargon */}
                <div className="text-center mb-10">
                    <h1 className="text-3xl font-bold mb-2 tracking-tight">
                        Sign in to Sidelith
                    </h1>
                    <p className="text-zinc-400">
                        AI memory for your codebase
                    </p>
                </div>

                {/* GitHub Button */}
                <button
                    onClick={handleGitHubLogin}
                    disabled={isLoading}
                    className="w-full h-12 rounded-full bg-white text-black flex items-center justify-center gap-3 font-semibold hover:bg-zinc-200 transition-all disabled:opacity-50"
                >
                    {isLoading ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                        <>
                            <Github className="w-5 h-5" />
                            Continue with GitHub
                        </>
                    )}
                </button>

                {error && (
                    <p className="text-red-400 text-sm mt-4 text-center bg-red-500/10 p-3 rounded">
                        {error}
                    </p>
                )}

                {/* Footer */}
                <p className="text-center text-xs text-zinc-500 mt-12">
                    By continuing, you agree to our{" "}
                    <Link href="/terms" className="text-zinc-400 hover:text-white underline underline-offset-4">
                        Terms
                    </Link>
                    {" "}and{" "}
                    <Link href="/privacy" className="text-zinc-400 hover:text-white underline underline-offset-4">
                        Privacy Policy
                    </Link>
                </p>
            </div>
        </div>
    );
}
