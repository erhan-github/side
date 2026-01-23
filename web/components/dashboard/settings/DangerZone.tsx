"use client";

import { Trash2, AlertTriangle } from "lucide-react";

export function DangerZone() {
    return (
        <div className="border border-red-900/30 bg-red-950/5 rounded-xl p-6">
            <h3 className="text-red-400 font-bold mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" /> Danger Zone
            </h3>

            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="text-sm text-zinc-400 max-w-2xl">
                    <strong className="text-red-200 block mb-1">Purge Registry Intelligence</strong>
                    Irreversibly wipe all context associated with your workspace from Sidelith's remote registry.
                    This does not affect your local project snapshots.
                </div>
                <button
                    onClick={() => confirm("Are you absolutely sure? This action cannot be undone.") && alert("Purge request initiated. (Stub)")}
                    className="bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/20 px-4 py-2 rounded-lg text-sm font-black transition-colors flex items-center gap-2 whitespace-nowrap uppercase italic tracking-tighter"
                >
                    <Trash2 className="w-4 h-4" /> Purge Cloud Registry
                </button>
            </div>
        </div>
    );
}
