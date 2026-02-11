"use client";

import { useEffect, useState } from "react";
import { Zap, Activity, Database, FileText } from "lucide-react";
import { CheckoutButton } from "@/components/dashboard/CheckoutButton";
import { createClient } from "@/lib/supabase/client";
import { UsageLedger } from "@/components/dashboard/UsageLedger";

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
    efficiency: number;
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
                const { data: { user } } = await supabase.auth.getUser();
                if (user) setUserEmail(user.email ?? null);

                const statsRes = await fetch('/api/dashboard/stats');
                if (statsRes.ok) {
                    const statsData = await statsRes.json();
                    setStats(statsData);
                }

                const ledgerRes = await fetch('/api/dashboard/ledger');
                if (ledgerRes.ok) {
                    const ledgerData = await ledgerRes.json();
                    setLedger(ledgerData);
                }
            } catch (err) {
                console.error("Dashboard fetch failed:", err);
            } finally {
                setLoading(false);
            }
        }

        fetchData();
        const interval = setInterval(fetchData, 10000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return null;

    return (
        <div className="min-h-screen bg-[#050505] text-white p-6 md:p-12 font-sans">
            <div className="max-w-6xl mx-auto space-y-12">

                {/* Header Area */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-white/5 pb-8">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight mb-2">Dashboard</h1>
                        <p className="text-zinc-500 text-sm font-medium">Your Side Unit usage and account status.</p>
                    </div>

                    <div className="flex gap-4 p-4 rounded-xl bg-white/[0.02] border border-white/5">
                        <div className="text-right">
                            <p className="text-[10px] uppercase text-zinc-600 tracking-widest font-black mb-1">Active Plan</p>
                            <p className="text-sm font-bold text-white uppercase">{stats?.tier || "Hobby"}</p>
                        </div>
                        <div className="w-[1px] bg-white/10" />
                        <div className="text-right">
                            <p className="text-[10px] uppercase text-zinc-600 tracking-widest font-black mb-1">Authenticated</p>
                            <p className="text-sm font-medium text-zinc-400 truncate max-w-[180px]">{userEmail || "Anonymous"}</p>
                        </div>
                    </div>
                </div>

                {/* Primary Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {/* Side Units Balance */}
                    <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors group flex flex-col justify-between min-h-[200px]">
                        <div>
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                                    <Zap className="w-5 h-5" />
                                </div>
                                <span className="text-xs font-bold uppercase tracking-[0.2em] text-zinc-500">Available Balance</span>
                            </div>

                            <div className="space-y-1 mb-6">
                                <div className="flex items-baseline gap-2">
                                    <span className="text-4xl font-bold text-white">{stats?.su_available.toLocaleString()}</span>
                                    <span className="text-zinc-600 text-sm font-medium">/ {stats?.su_limit?.toLocaleString()} SU</span>
                                </div>
                            </div>
                        </div>

                        <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-emerald-500/80 transition-all duration-1000 ease-out shadow-[0_0_8px_rgba(16,185,129,0.4)]"
                                style={{ width: `${((stats?.su_available || 0) / (stats?.su_limit || 1)) * 100}%` }}
                            />
                        </div>
                    </div>

                    <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors group flex flex-col justify-between min-h-[200px]">
                        <div>
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                                    <Activity className="w-5 h-5" />
                                </div>
                                <span className="text-xs font-bold uppercase tracking-[0.2em] text-zinc-500">Usage Metrics</span>
                            </div>

                            <div className="space-y-1 mb-6">
                                <div className="flex items-baseline gap-2">
                                    <span className="text-4xl font-bold text-white">{stats?.su_used.toLocaleString()}</span>
                                    <span className="text-zinc-600 text-sm font-medium">SUs Consumed</span>
                                </div>
                            </div>
                        </div>
                        <div className="text-xs text-zinc-600 font-medium">Real-time telemetry active</div>
                    </div>

                    {/* Quick Upgrade/Promotion */}
                    {stats?.tier?.toUpperCase() !== "ELITE" && (
                        <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between hover:border-blue-500/20 transition-colors group min-h-[200px]">
                            <div className="relative z-10">
                                <div className="flex items-center gap-2 mb-4">
                                    <div className="p-1.5 rounded-md bg-blue-500/10 text-blue-400">
                                        <Zap className="w-3.5 h-3.5" />
                                    </div>
                                    <span className="text-xs font-bold text-blue-400 uppercase tracking-widest">Growth Tier</span>
                                </div>
                                <h3 className="text-lg font-bold text-white mb-2">Go Elite</h3>
                                <p className="text-sm text-zinc-500 leading-relaxed font-medium">Unlock 25,000 SUs and priority indexing.</p>
                            </div>
                            <CheckoutButton
                                variantId={process.env.NEXT_PUBLIC_LEMONSQUEEZY_VARIANT_ID_ELITE || ""}
                                label="Upgrade Account"
                                className="w-full bg-white text-black hover:bg-zinc-200 transition-all rounded-xl h-10 text-xs font-bold mt-4 shadow-sm"
                            />
                        </div>
                    )}
                </div>

                {/* Ledger Section */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2 space-y-6">
                        <div className="flex items-center gap-3 px-1">
                            <div className="w-4 h-4 rounded-[4px] bg-emerald-500/10 flex items-center justify-center">
                                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                            </div>
                            <h2 className="text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-500">DNA Activity Stream</h2>
                        </div>
                        <UsageLedger entries={ledger} />
                    </div>

                    <div className="space-y-6">
                        <div className="p-6 rounded-2xl border border-white/5 bg-white/[0.01]">
                            <div className="flex items-center gap-2 mb-4">
                                <Database className="w-4 h-4 text-zinc-500" />
                                <h3 className="text-sm font-bold text-white">System Status</h3>
                            </div>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between text-xs">
                                    <span className="text-zinc-500">Local Index</span>
                                    <span className="text-emerald-400 font-medium">Synchronized</span>
                                </div>
                                <div className="flex items-center justify-between text-xs">
                                    <span className="text-zinc-500">Cloud Link</span>
                                    <span className="text-blue-400 font-medium">Encrypted</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="pt-12 border-t border-white/5 text-center">
                    <p className="text-[10px] text-zinc-700 font-mono uppercase tracking-[0.2em]">
                        Sidelith v1.1.0
                    </p>
                </div>
            </div>
        </div>
    );
}
