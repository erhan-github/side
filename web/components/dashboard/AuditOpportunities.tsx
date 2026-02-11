"use client";

import { Copy, ArrowRight, Sparkles } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

// Derived from ACTUAL Audit Run (2026-01-20)
const OPPORTUNITIES = [
    {
        id: "DEEP-SEC-001",
        emoji: "✍️",
        title: "Fix Critical Auth Bypass in Magic Link Route",
        desc: "Logic flaw in `route.ts` allows bypass when Supabase is unconfigured.",
        prompt: "Refactor `web/app/api/auth/magic-link/route.ts` to ensure the `isSupabaseConfigured` check properly blocks unauthenticated access and doesn't return a success response prematurely.",
        impact: "Critical Security"
    },
    // ... (rest of the array content is actually fine, but I need to make sure I don't cut it off. The view_file showed lines 1-127. I will use a targeted replacement for the start of the file and the function definition separately or just replace the top part if I can match it unique enough.
    // Actually, I can just replace the top block and the function definition block.
    // Let's do it in one go if they are close, or two chunks.
    // Lines 7-8 and line 59.

    {
        id: "PERF-001",
        emoji: "✍️",
        title: "Optimize N+1 Queries in Onboarding Flow",
        desc: "Detected loop-based database queries in `onboarding.py`.",
        prompt: "Refactor `backend/src/side/onboarding.py` to use batch queries or `prefetch_related` for user data loading to eliminate the N+1 query performance bottleneck.",
        impact: "High Performance"
    },
    {
        id: "SEC-006",
        emoji: "✍️",
        title: "Enforce HTTPS for External Integrations",
        desc: "Found non-HTTPS URLs in feed registry and error handlers.",
        prompt: "Scan `backend/src/side/intel/feed_registry.py` and update all hardcoded feed URLs to use HTTPS to prevent man-in-the-middle attacks.",
        impact: "Security Handling"
    },
    {
        id: "ARCH-002",
        emoji: "✍️",
        title: "Enforce Layer Boundary in `intel/`",
        desc: "Detected direct DB access in Intelligence Service.",
        prompt: "Check `backend/src/side/intel/strategist.py` for direct import of `SimplifiedDatabase`. This violates the layered architecture rules. Refactor to use the abstract `SchemaStore` repository pattern instead.",
        impact: "Architecture Rule"
    },
    {
        id: "DEVOPS-005",
        emoji: "✍️",
        title: "Missing Health Check Probe",
        desc: "Docker container lacks healthcheck definition.",
        prompt: "Update `backend/Dockerfile` to include a `HEALTHCHECK` instruction that pings `http://localhost:8000/health` so the orchestrator can restart the service if it hangs.",
        impact: "Resiliency"
    },
    {
        id: "CQ-003",
        emoji: "✍️",
        title: "Split Monolithic `simple_db.py`",
        desc: "File exceeds 1,900 lines. High maintenance risk.",
        prompt: "Refactor `backend/src/side/storage/simple_db.py` by extracting the schema initialization and query helper methods into separate modules within a `storage/` package.",
        impact: "Maintainability"
    }
];

export function AuditOpportunities() {
    const [copiedId, setCopiedId] = useState<string | null>(null);

    const handleCopy = (id: string, prompt: string) => {
        navigator.clipboard.writeText(prompt);
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000);
    };

    return (
        <div className="bg-[#0c0c0e] border border-white/10 rounded-xl overflow-hidden flex flex-col h-full">
            <div className="p-5 border-b border-white/5 flex items-center justify-between bg-zinc-900/30 backdrop-blur-sm">
                <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-amber-400" />
                    <h3 className="text-sm font-medium text-white">Strategic Opportunities</h3>
                </div>
                <span className="text-[10px] bg-amber-500/10 text-amber-400 px-2 py-0.5 rounded border border-amber-500/20">
                    High Leverage
                </span>
            </div>

            <div className="divide-y divide-white/5">
                {OPPORTUNITIES.map((opp) => (
                    <div key={opp.id} className="group p-4 hover:bg-white/[0.02] transition-colors relative">
                        <div className="flex items-start gap-4">
                            <div className="text-2xl pt-1 select-none grayscale group-hover:grayscale-0 transition-all opacity-70 group-hover:opacity-100 scale-95 group-hover:scale-110 duration-300">
                                {opp.emoji}
                            </div>

                            <div className="flex-1 min-w-0">
                                <div className="flex items-start justify-between mb-1">
                                    <h4 className="text-sm font-medium text-zinc-200 group-hover:text-white transition-colors">
                                        {opp.title}
                                    </h4>
                                    <span className="text-[10px] text-zinc-600 font-mono uppercase tracking-wider group-hover:text-zinc-500">
                                        {opp.impact}
                                    </span>
                                </div>
                                <p className="text-xs text-zinc-500 line-clamp-1 mb-2">
                                    {opp.desc}
                                </p>

                                {/* Prompt Area (Reveals on Hover/Focus) */}
                                <div className="bg-zinc-950/50 rounded-lg p-2 border border-white/5 flex items-center gap-3">
                                    <code className="text-[10px] text-zinc-400 font-mono flex-1 truncate">
                                        {opp.prompt}
                                    </code>
                                    <button
                                        onClick={() => handleCopy(opp.id, opp.prompt)}
                                        className={cn(
                                            "p-1.5 rounded transition-colors flex-shrink-0",
                                            copiedId === opp.id
                                                ? "bg-emerald-500/10 text-emerald-400"
                                                : "hover:bg-white/10 text-zinc-500 hover:text-white"
                                        )}
                                        title="Copy Prompt"
                                    >
                                        {copiedId === opp.id ? "Copied!" : <Copy className="w-3 h-3" />}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
