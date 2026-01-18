"use client";

import { Loader2, Sparkles } from "lucide-react";
import { useState } from "react";

export function RefillButton() {
    const [loading, setLoading] = useState(false);

    const handleRefill = async () => {
        try {
            setLoading(true);
            const res = await fetch("/api/stripe/checkout", {
                method: "POST",
                body: JSON.stringify({ quantity: 1 }),
            });

            const { url } = await res.json();
            if (url) {
                window.location.href = url;
            }
        } catch (error) {
            console.error("Refill failed", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <button
            onClick={handleRefill}
            disabled={loading}
            className="group relative w-full py-2.5 text-xs font-bold uppercase tracking-widest bg-white text-black rounded-lg hover:shadow-[0_0_20px_rgba(255,255,255,0.3)] transition-all duration-300 flex items-center justify-center gap-2 overflow-hidden"
        >
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-zinc-200 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />

            {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
                <>
                    <Sparkles className="w-3.5 h-3.5 text-zinc-400 group-hover:text-black transition-colors" />
                    <span>Purchase Strategic Capacity</span>
                </>
            )}
        </button>
    );
}
