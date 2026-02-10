"use client";

import { Terminal, Clock } from "lucide-react";

interface LedgerEntry {
    type: string;
    description: string;
    outcome: string;
    timestamp: string;
    cost: number;
}

interface UsageLedgerProps {
    entries: LedgerEntry[];
}

export function UsageLedger({ entries }: UsageLedgerProps) {
    if (entries.length === 0) {
        return (
            <div className="bg-zinc-900/30 border border-white/5 rounded-xl p-12 text-center">
                <p className="text-zinc-500 font-mono text-xs uppercase tracking-widest">No activities recorded yet.</p>
            </div>
        );
    }

    return (
        <div className="bg-black border border-white/10 rounded-xl overflow-hidden shadow-2xl">
            <div className="h-10 bg-white/5 border-b border-white/5 flex items-center justify-between px-6">
                <div className="flex items-center gap-2">
                    <Terminal className="w-3 h-3 text-zinc-500" />
                    <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest font-mono">Billing Ledger</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                    <span className="text-[10px] text-zinc-600 font-mono uppercase tracking-widest">Synchronized</span>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                    <thead className="bg-white/[0.01] text-zinc-500 font-mono uppercase tracking-wider border-b border-white/5">
                        <tr>
                            <th className="px-6 py-4 font-bold">Operation</th>
                            <th className="px-6 py-4 font-bold">Details</th>
                            <th className="px-6 py-4 font-bold text-right">Cost</th>
                            <th className="px-6 py-4 font-bold text-right">Timestamp</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {entries.map((entry, i) => (
                            <tr key={i} className="hover:bg-white/[0.02] transition-colors group">
                                <td className="px-6 py-4 font-mono">
                                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold ${entry.cost > 50 ? 'bg-orange-500/10 text-orange-400' : 'bg-blue-500/10 text-cyan-400'
                                        }`}>
                                        {entry.type}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-zinc-400 font-mono max-w-sm truncate group-hover:text-zinc-300 transition-colors">
                                    {entry.description}
                                </td>
                                <td className="px-6 py-4 text-right text-zinc-400 font-mono font-bold">
                                    <span className={entry.cost > 0 ? "text-zinc-300" : "text-emerald-400/60"}>
                                        {entry.cost > 0 ? `-${entry.cost}` : "FREE"}
                                    </span>
                                    <span className="text-[10px] text-zinc-600 ml-1">SU</span>
                                </td>
                                <td className="px-6 py-4 text-right text-zinc-500 font-mono">
                                    {new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
