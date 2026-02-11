"use client";

import { CreditCard, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

type BillingOverviewProps = {
    used: number;
    limit: number;
    unbilled?: number;
    planName?: string; // e.g. "PRO Plan"
};

export function BillingOverview({ used, limit, unbilled = 0, planName = "PRO Plan" }: BillingOverviewProps) {
    const percentage = Math.min(100, (used / limit) * 100);
    // Cursor uses a blue/purple gradient for their "On-Demand" usage
    // We will use Side's Blue/Purple neon brand

    return (
        <div className="bg-[#0c0c0e] border border-white/10 rounded-xl p-5 relative overflow-hidden group h-full flex flex-col justify-between">
            {/* Header */}
            <div className="flex justify-between items-start z-10 relative">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                        <CreditCard className="w-4 h-4 text-blue-400" />
                    </div>
                    <div>
                        <h3 className="text-sm font-medium text-white leading-tight">Monthly Allowance</h3>
                        <p className="text-xs text-zinc-500 mt-0.5">{planName} • {limit.toLocaleString()} CP</p>
                    </div>
                </div>

                {/* Upgrade / Manage Button - Premium Ghost Style */}
                <button
                    onClick={() => alert("Billing integration coming soon (Lemon Squeezy Bypass Active)")}
                    className="text-[10px] font-medium text-zinc-400 hover:text-white border border-white/5 hover:border-white/20 bg-white/5 hover:bg-white/10 px-2.5 py-1.5 rounded transition-all"
                >
                    Manage Limit
                </button>
            </div>

            {/* Middle Section: Progress */}
            <div className="flex flex-col justify-center flex-1 py-4">
                {/* Segmented Progress Bar (Cursor Style) */}
                <div className="flex bg-zinc-800/30 rounded-full h-2 overflow-hidden p-[1px] gap-[1px]">
                    {[...Array(20)].map((_, i) => {
                        const blockValue = 100 / 20; // 5% per block
                        const isFilled = percentage >= (i + 1) * blockValue;

                        return (
                            <div
                                key={i}
                                className={cn(
                                    "flex-1 rounded-[1px] transition-all duration-300",
                                    isFilled ? "bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]" : "bg-white/5"
                                )}
                            />
                        )
                    })}
                </div>
            </div>

            {/* Footer Stats */}
            <div className="flex justify-between items-end">
                <div className="flex flex-col">
                    <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-mono mb-1">Used</span>
                    <div className="text-2xl font-bold text-white font-mono tracking-tight leading-none">
                        {used.toLocaleString()} <span className="text-zinc-600 text-sm">CP</span>
                    </div>
                </div>

                <div className="flex flex-col items-end">
                    <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-mono mb-1">Unbilled</span>
                    {/* Mid-Month Invoicing Simulation */}
                    <div className="text-xl font-bold text-white font-mono tracking-tight flex items-center gap-2 leading-none">
                        ${unbilled.toFixed(2)} <TrendingUp className="w-3 h-3 text-zinc-600" />
                    </div>
                </div>
            </div>

            {/* Decorative Glow */}
            <div className="absolute -top-10 -right-10 w-40 h-40 bg-blue-500/5 blur-[60px] rounded-full pointer-events-none group-hover:bg-blue-500/10 transition-colors duration-500" />
        </div>
    );
}
