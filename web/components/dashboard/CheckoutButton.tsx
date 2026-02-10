"use client";

import { useState } from "react";
import { Zap } from "lucide-react";
import { cn } from "@/lib/utils";
import { createClient } from "@/lib/supabase/client";

interface CheckoutButtonProps {
    variantId: string;
    label: string;
    className?: string;
    variant?: "default" | "outline" | "purple";
}

export function CheckoutButton({ variantId, label, className, variant = "default" }: CheckoutButtonProps) {
    const [isLoading, setIsLoading] = useState(false);

    const handleCheckout = async () => {
        try {
            setIsLoading(true);

            // 1. Proactive Auth Check
            const supabase = createClient();
            const { data: { user } } = await supabase.auth.getUser();

            if (!user) {
                // If not logged in, redirect to login with this variant as context
                // We'll use a standard redirect to /login
                window.location.href = `/login?next=pricing&ref=${variantId}`;
                return;
            }

            // 2. Proceed to Backend Checkout API
            const response = await fetch("/api/lemonsqueezy/checkout", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ variantId }),
            });

            const data = await response.json();

            if (response.ok && data.url) {
                window.location.href = data.url;
            } else {
                console.error("Checkout failed:", data.error || "No URL");
                alert(`Checkout failed: ${data.error || "Please try again."}`);
            }
        } catch (error) {
            console.error("Checkout error:", error);
            alert("Connection error: Unable to reach the billing server. Please check your internet or try again later.");
        } finally {
            setIsLoading(false);
        }
    };

    const variants = {
        default: "bg-white text-black hover:bg-zinc-200",
        outline: "border border-white/10 text-white hover:bg-white hover:text-black",
        purple: "bg-purple-600 text-white hover:bg-purple-500 shadow-[0_0_30px_-5px_theme(colors.purple.600)]",
    };

    return (
        <button
            onClick={handleCheckout}
            disabled={isLoading}
            className={cn(
                "w-full h-12 rounded-full font-black uppercase text-xs tracking-[0.2em] transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed",
                variants[variant],
                className
            )}
        >
            {isLoading ? (
                <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
            ) : (
                <Zap className="w-4 h-4" />
            )}
            {isLoading ? "Provisioning..." : label}
        </button>
    );
}
