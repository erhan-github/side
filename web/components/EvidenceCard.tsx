import { motion } from "framer-motion";
import { AlertCircle, CheckCircle, ShieldAlert } from "lucide-react";

export function EvidenceCard() {
    return (
        <div className="w-full max-w-xl mx-auto rounded-xl border border-white/10 bg-zinc-900 shadow-2xl overflow-hidden font-mono text-sm">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-white/5 border-b border-white/5">
                <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>
                <div className="text-zinc-500 text-xs font-bold uppercase tracking-widest">Sidelith D-700</div>
            </div>

            {/* Body */}
            <div className="p-6 space-y-6">

                {/* Command */}
                <div className="flex gap-3 items-center opacity-70">
                    <span className="text-emerald-500">➜</span>
                    <span className="text-zinc-100">git commit -m "add stripe implementation"</span>
                </div>

                {/* Sidelith Interception */}
                <div className="relative pl-4 border-l-2 border-red-500/50 space-y-4">

                    {/* The Catch */}
                    <div className="bg-red-950/30 border border-red-500/20 rounded-lg p-4">
                        <div className="flex items-start gap-3">
                            <ShieldAlert className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                            <div>
                                <h4 className="text-red-400 font-bold mb-1">BLOCKED: Sovereign Integrity Violation</h4>
                                <p className="text-zinc-300 mb-2">Detailed forensic analysis detected a high-risk pattern.</p>

                                <div className="bg-black/50 rounded p-2 text-xs text-red-300 font-mono mb-2">
                                    &gt; SEC-002: Hardcoded Secret ('sk_live_...')<br />
                                    &gt; STRAT-009: Deviation from ARCHITECTURE.md
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* The Remediation */}
                    <div className="flex items-center gap-2 text-zinc-400 text-xs">
                        <AlertCircle className="w-4 h-4 text-zinc-500" />
                        <span>Action Required: Scrub secrets & align with 'Payments Module V2' spec.</span>
                    </div>

                </div>

            </div>
        </div>
    );
}
