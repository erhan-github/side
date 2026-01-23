"use client";

import { Eye } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface GhostModeSectionProps {
    initialEnabled: boolean;
}

export function GhostModeSection({ initialEnabled }: GhostModeSectionProps) {
    const [ghostMode, setGhostMode] = useState(initialEnabled);

    return (
        <div className={cn(
            "border rounded-2xl p-6 md:p-8 transition-all duration-300 relative overflow-hidden",
            ghostMode ? "bg-emerald-950/10 border-emerald-500/30" : "bg-[#0c0c0e] border-white/10"
        )}>
            {ghostMode && (
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 pointer-events-none" />
            )}

            <div className="flex flex-col md:flex-row justify-between items-center gap-8 relative z-10">
                <div className="flex-1">
                    <h3 className="text-xl font-bold text-white flex items-center gap-3 mb-2">
                        <Eye className={cn("w-6 h-6", ghostMode ? "text-emerald-400" : "text-zinc-500")} />
                        Ghost Mode
                        {ghostMode && <span className="bg-emerald-500/20 text-emerald-400 text-xs px-2 py-0.5 rounded border border-emerald-500/30">ACTIVE</span>}
                    </h3>
                    <p className="text-zinc-400 text-sm leading-relaxed max-w-2xl">
                        When active, Sidelith creates an "air gap" for your intelligence. All external API calls (Anthropic, OpenAI) are intercepted.
                        Inference is routed strictly to your local models or secure cached snapshots.
                    </p>
                </div>

                <button
                    onClick={() => setGhostMode(!ghostMode)}
                    className={cn(
                        "relative inline-flex h-8 w-14 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:ring-offset-2 focus:ring-offset-black",
                        ghostMode ? "bg-emerald-600" : "bg-zinc-700"
                    )}
                >
                    <span className={cn(
                        "pointer-events-none inline-block h-7 w-7 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out",
                        ghostMode ? "translate-x-6" : "translate-x-0"
                    )} />
                </button>
            </div>
        </div>
    );
}
