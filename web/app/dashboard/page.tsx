"use client";

import { useEffect, useState } from "react";
import { Zap, Activity, Clock, ShieldCheck, Terminal, Cpu, Database } from "lucide-react";
import { CheckoutButton } from "@/components/dashboard/CheckoutButton";
import { createClient } from "@/lib/supabase/client";

interface LedgerEntry {
    type: string;
    description: string;
    outcome: string;
    timestamp: string;
    cost: number;
}

interface Stats {
    su_available: number;
    su_used: number;
    tier: string;
    efficiency: number; // 0-100
    su_limit: number;
    saved_tokens: number;
}

export default function DashboardPage() {
    const [ledger, setLedger] = useState<LedgerEntry[]>([]);
    const [stats, setStats] = useState<Stats | null>(null);
    const [loading, setLoading] = useState(true);
    const [userEmail, setUserEmail] = useState<string | null>(null);

    const supabase = createClient();

    useEffect(() => {
        async function fetchData() {
            try {
                // 1. Auth Check (Client-Side)
                const { data: { user } } = await supabase.auth.getUser();
                if (user) setUserEmail(user.email ?? null);

                // 2. Fetch Real System Stats
                const statsRes = await fetch('/api/dashboard/stats');
                if (statsRes.ok) {
                    const statsData = await statsRes.json();
                    setStats(statsData);
                }

                // 3. Fetch Real Ledger
                const ledgerRes = await fetch('/api/dashboard/ledger');
                if (ledgerRes.ok) {
                    const ledgerData = await ledgerRes.json();
                    setLedger(ledgerData);
                }
            } catch (err) {
                console.error("Failed to fetch dashboard data:", err);
            } finally {
                setLoading(false);
            }
        }

        fetchData();
        const interval = setInterval(fetchData, 10000); // 10s polling for "Live" feel
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-8 h-8 border-t-2 border-cyan-500 rounded-full animate-spin"></div>
                    <p className="text-zinc-500 font-mono text-xs uppercase tracking-widest">Initializing Sidelith HUD...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-black text-white p-6 md:p-12 font-mono">
            <div className="max-w-6xl mx-auto space-y-12">

                {/* 1. TOP HEADER (STATUS BAR) */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-end border-b border-white/5 pb-8 gap-6">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                            </span>
                            <span className="text-[10px] uppercase tracking-[0.2em] text-emerald-500/80 font-bold">Focal Engine Active</span>
                        </div>
                        <h1 className="text-3xl md:text-4xl font-sans font-bold tracking-tight text-white/90">
                            Pulse <span className="text-white/20 font-light">HUD</span>
                        </h1>
                    </div>

                    <div className="flex gap-4 md:gap-8 text-right">
                        <div>
                            <p className="text-[10px] uppercase text-zinc-600 tracking-wider font-bold mb-1">Current Tier</p>
                            <p className="text-sm font-bold text-cyan-400">{stats?.tier} <span className="text-zinc-600 text-[10px]">PLAN</span></p>
                        </div>
                        <div>
                            <p className="text-[10px] uppercase text-zinc-600 tracking-wider font-bold mb-1">User</p>
                            <p className="text-sm text-zinc-400 truncate max-w-[150px]">{userEmail}</p>
                        </div>
                    </div>
                </div>

                {/* 2. MAIN METRICS GRID */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

                    {/* CARD 1: SIDE UNITS (BALANCE) */}
                    <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-6 relative overflow-hidden group hover:border-white/10 transition-colors">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Database className="w-16 h-16 text-cyan-500" />
                        </div>
                        <p className="text-[10px] uppercase text-zinc-500 tracking-widest font-bold mb-4">Side Units (SUs)</p>
                        <div className="flex items-baseline gap-2 mb-2">
                            <span className="text-5xl font-sans font-bold text-white tracking-tight">{stats?.su_available.toLocaleString()}</span>
                            <span className="text-sm text-zinc-600 font-bold">/ {stats?.su_limit?.toLocaleString()}</span>
                        </div>
                        <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden mb-4">
                            <div className="h-full bg-cyan-500/50" style={{ width: `${((stats?.su_available || 0) / (stats?.su_limit || 1)) * 100}%` }}></div>
                        </div>
                        <p className="text-xs text-zinc-400">
                            <span className="text-emerald-400">+{stats?.su_limit?.toLocaleString()}</span> monthly refresh in 12 days.
                        </p>
                    </div>

                    {/* CARD 2: EFFICIENCY (PERFORMANCE) */}
                    <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-6 relative overflow-hidden group hover:border-white/10 transition-colors">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Cpu className="w-16 h-16 text-emerald-500" />
                        </div>
                        <p className="text-[10px] uppercase text-zinc-500 tracking-widest font-bold mb-4">Context Efficiency</p>
                        <div className="flex items-baseline gap-2 mb-6">
                            <span className="text-5xl font-sans font-bold text-white tracking-tight">{stats?.efficiency}%</span>
                        </div>
                        <p className="text-xs text-zinc-400">
                            Fractal Indexing saved <span className="text-white">{stats?.saved_tokens?.toLocaleString() || 0} tokens</span> this month.
                        </p>
                    </div>

                    {/* CARD 3: UPGRADE ALERT / STATUS */}
                    <div className="bg-gradient-to-br from-blue-900/10 to-transparent border border-blue-500/20 rounded-2xl p-6 flex flex-col justify-center items-center text-center relative overflow-hidden">
                        <div className="absolute inset-0 bg-blue-500/5 animate-pulse pointer-events-none" />
                        <Zap className="w-8 h-8 text-blue-400 mb-3" />
                        <h3 className="text-sm font-bold text-white mb-1">Unlock Deep Meaning</h3>
                        <p className="text-[10px] text-zinc-400 mb-4 max-w-[200px]">Upgrade to Elite for 10x throughput and Cloud Distillation.</p>
                        <CheckoutButton
                            variantId={process.env.NEXT_PUBLIC_VARIANT_ID_PRO || ""}
                            label="Upgrade Plan"
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-lg transition-colors"
                        />
                    </div>
                </div>

                {/* 3. FLIGHT RECORDER (LEDGER) */}
                <div className="bg-black border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
                    <div className="h-10 bg-white/5 border-b border-white/5 flex items-center justify-between px-6">
                        <div className="flex items-center gap-2">
                            <Terminal className="w-3 h-3 text-zinc-500" />
                            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Flight Recorder (Live)</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                            <span className="text-[10px] text-zinc-600 font-mono">REC</span>
                        </div>
                    </div>

                    <div className="p-0">
                        <table className="w-full text-left text-xs">
                            <thead className="bg-white/[0.01] text-zinc-500 font-mono uppercase tracking-wider border-b border-white/5">
                                <tr>
                                    <th className="px-6 py-3 font-normal font-bold">Event Type</th>
                                    <th className="px-6 py-3 font-normal font-bold">Description</th>
                                    <th className="px-6 py-3 font-normal font-bold text-right">Cost</th>
                                    <th className="px-6 py-3 font-normal font-bold text-right">Time</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {ledger.map((entry, i) => (
                                    <tr key={i} className="hover:bg-white/[0.02] transition-colors group">
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2 py-1 rounded text-[10px] font-bold ${entry.outcome === 'WARN' ? 'bg-yellow-500/10 text-yellow-500' : 'bg-blue-500/10 text-cyan-400'
                                                }`}>
                                                {entry.type}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-zinc-400 font-mono group-hover:text-zinc-300 transition-colors">
                                            {entry.description}
                                        </td>
                                        <td className="px-6 py-4 text-right text-zinc-500 font-mono">
                                            -{entry.cost} SU
                                        </td>
                                        <td className="px-6 py-4 text-right text-zinc-600 font-mono">
                                            {new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div className="text-center">
                    <p className="text-[10px] text-zinc-700 font-mono">
                        Sidelith Focal Engine v3.1.0 · Connected to Stockholm Node
                    </p>
                </div>

            </div>
        </div>
    );
}
