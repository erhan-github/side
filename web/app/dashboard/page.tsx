"use client";

import { useEffect, useState } from "react";
import { Zap, Activity, Clock, ShieldCheck } from "lucide-react";
import { CheckoutButton } from "@/components/dashboard/CheckoutButton";
import { createClient } from "@/lib/supabase/client";

interface LedgerEntry {
    type: string;
    outcome: string;
    timestamp: string;
}

interface Stats {
    tokens_available: number;
    tokens_used: number;
    tier: string;
}

export default function DashboardPage() {
    const [ledger, setLedger] = useState<LedgerEntry[]>([]);
    const [stats, setStats] = useState<Stats | null>(null);
    const [loading, setLoading] = useState(true);
    const [userEmail, setUserEmail] = useState<string | null>(null);

    const supabase = createClient();

    useEffect(() => {
        async function fetchData() {
            const { data: { user } } = await supabase.auth.getUser();
            if (user) setUserEmail(user.email ?? null);

            try {
                // In production, these should be environment variables
                const API_BASE = "http://localhost:8080/api";

                const [ledgerRes, statsRes] = await Promise.all([
                    fetch(`${API_BASE}/ledger`),
                    fetch(`${API_BASE}/stats`)
                ]);

                if (ledgerRes.ok && statsRes.ok) {
                    setLedger(await ledgerRes.json());
                    setStats(await statsRes.json());
                }
            } catch (err) {
                console.error("Failed to fetch Sovereign Ledger:", err);
            } finally {
                setLoading(false);
            }
        }

        fetchData();
        // Poll every 30 seconds for live updates
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-8 h-8 border-t-2 border-cyan-500 rounded-full animate-spin"></div>
                    <p className="text-zinc-500 font-mono text-xs uppercase tracking-widest">Hydrating Secure Session...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-black text-white p-8">
            <div className="max-w-4xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex justify-between items-end border-b border-white/10 pb-6">
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <div className="w-3 h-3 bg-emerald-500 rounded-sm" />
                            <span className="text-xs uppercase tracking-[0.3em] text-zinc-500 font-bold">Sidelith Core</span>
                        </div>
                        <h1 className="text-4xl font-bold tracking-tighter">Strategic <span className="text-zinc-500 font-light text-2xl ml-2">Ledger</span></h1>
                        <p className="text-zinc-400 mt-2 italic text-sm">User: {userEmail}</p>
                    </div>
                </div>

                {/* Main Utility Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* SU BALANCE CARD */}
                    <div className="bg-zinc-900 border border-white/10 rounded-xl p-8 flex flex-col justify-between h-full">
                        <div>
                            <h3 className="text-xs uppercase tracking-widest text-zinc-500 font-black mb-4">Strategic Throughput</h3>
                            <div className="flex items-baseline gap-2">
                                <span className="text-6xl font-black tracking-tighter text-cyan-400">
                                    {stats?.tokens_available.toLocaleString() ?? "---"}
                                </span>
                                <span className="text-zinc-600 font-bold uppercase tracking-tighter">SU</span>
                            </div>
                            <p className="text-[10px] text-zinc-500 mt-2 uppercase tracking-widest font-bold">Available Strategic Units</p>
                        </div>

                        <div className="mt-8">
                            <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-cyan-500 transition-all duration-1000"
                                    style={{
                                        width: `${Math.min(100, ((stats?.tokens_used ?? 0) / ((stats?.tokens_available ?? 1) + (stats?.tokens_used ?? 0))) * 100)}%`
                                    }}
                                />
                            </div>
                            <div className="flex justify-between mt-2 text-[10px] uppercase font-bold text-zinc-600">
                                <span>{stats?.tokens_used.toLocaleString()} Used</span>
                                <span>{stats?.tier ?? "Free"}</span>
                            </div>
                        </div>
                    </div>

                    {/* UPGRADE CARD */}
                    <div className="bg-zinc-900 border border-white/10 rounded-xl p-8 flex flex-col justify-center items-center text-center group">
                        <div className="w-12 h-12 bg-cyan-500/10 rounded-full flex items-center justify-center mb-4 group-hover:bg-cyan-500/20 transition-all">
                            <Zap className="w-6 h-6 text-cyan-500" />
                        </div>
                        <h3 className="font-bold text-lg mb-4 uppercase tracking-tighter italic">Evolve to Pro</h3>
                        <p className="text-xs text-zinc-500 mb-6">Unlimited Sovereign Watchers + Priority Forensic Compute.</p>
                        <CheckoutButton
                            variantId={process.env.NEXT_PUBLIC_VARIANT_ID_PRO || ""}
                            label="EVOLVE NOW ($20)"
                        />
                    </div>
                </div>

                {/* TRANSACTION LEDGER */}
                <div className="bg-zinc-900 border border-white/10 rounded-xl p-8">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-xs uppercase tracking-widest text-zinc-500 font-black">Execution Log</h3>
                        <div className="flex items-center gap-2 text-[10px] text-zinc-600 font-bold tracking-widest">
                            <Clock className="w-3 h-3" /> LIVE PULSE
                        </div>
                    </div>

                    <div className="space-y-4">
                        {ledger.length > 0 ? (
                            ledger.map((tx, i) => (
                                <div key={i} className="flex items-center justify-between py-3 border-b border-white/5 last:border-0 hover:bg-white/[0.02] -mx-4 px-4 rounded-lg transition-colors">
                                    <div className="flex items-center gap-4">
                                        <div className={`w-2 h-2 rounded-full ${tx.outcome === "PASS" ? "bg-emerald-500" : "bg-red-500"}`} />
                                        <div>
                                            <p className="text-sm font-bold text-white uppercase tracking-tighter">{tx.type}</p>
                                            <p className="text-[10px] text-zinc-500 uppercase">
                                                {new Date(tx.timestamp).toLocaleTimeString()} · {new Date(tx.timestamp).toLocaleDateString()}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm font-mono text-zinc-400">-5 SU</p>
                                        <p className={`text-[10px] uppercase font-black ${tx.outcome === "PASS" ? "text-emerald-400" : "text-red-400"}`}>
                                            {tx.outcome}
                                        </p>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="py-12 text-center">
                                <Activity className="w-8 h-8 text-zinc-800 mx-auto mb-4" />
                                <p className="text-xs text-zinc-600 uppercase tracking-widest font-bold">No pulse events detected</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
