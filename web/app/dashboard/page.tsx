"use client";

import { useEffect, useState } from "react";
import { Zap, Activity, ShieldCheck, Database, LayoutGrid } from "lucide-react";
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
        <div className="min-h-screen bg-black text-white p-6 md:p-12 font-sans">
            <div className="max-w-6xl mx-auto space-y-12">

                {/* Header Area */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight mb-2">Dashboard</h1>
                        <p className="text-zinc-500 text-sm">Your Side Unit usage and account status.</p>
                    </div>

                    <div className="flex gap-4 p-4 rounded-xl bg-zinc-900/50 border border-white/5">
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
                    <div className="bg-zinc-900/30 border border-white/5 rounded-2xl p-6 hover:bg-zinc-900/40 transition-colors group">
                        <div className="flex items-center justify-between mb-8">
                            <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 shadow-[0_0_15px_rgba(6,182,212,0.1)]">
                                <Database className="w-5 h-5 text-cyan-400" />
                            </div>
                            <CheckoutButton
                                variantId={process.env.NEXT_PUBLIC_LEMONSQUEEZY_VARIANT_ID_REFILL || ""}
                                label="Refill"
                                className="h-8 px-4 text-[10px] uppercase tracking-widest font-bold"
                            />
                        </div>

                        <div className="space-y-1 mb-6">
                            <p className="text-[10px] uppercase text-zinc-500 tracking-widest font-bold">Available Balance</p>
                            <div className="flex items-baseline gap-2">
                                <span className="text-4xl font-bold text-white">{stats?.su_available.toLocaleString()}</span>
                                <span className="text-zinc-600 text-sm font-mono">/ {stats?.su_limit?.toLocaleString()} SUs</span>
                            </div>
                        </div>

                        <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-cyan-500 transition-all duration-1000 ease-out"
                                style={{ width: `${((stats?.su_available || 0) / (stats?.su_limit || 1)) * 100}%` }}
                            />
                        </div>
                    </div>


                    {/* Quick Upgrade/Promotion */}
                    {stats?.tier?.toUpperCase() !== "ELITE" && (
                        <div className="bg-gradient-to-br from-blue-900/20 to-transparent border border-blue-500/20 rounded-2xl p-6 relative overflow-hidden flex flex-col justify-between">
                            <div className="relative z-10">
                                <div className="flex items-center gap-2 mb-4">
                                    <Zap className="w-4 h-4 text-blue-400" />
                                    <span className="text-[10px] font-bold text-blue-400 uppercase tracking-widest">Growth Tier</span>
                                </div>
                                <h3 className="text-white font-bold mb-1">Go Elite</h3>
                                <p className="text-xs text-zinc-500 line-clamp-2">Unlock 25,000 SUs, Cloud Distillation, and Priority Indexing.</p>
                            </div>
                            <CheckoutButton
                                variantId={process.env.NEXT_PUBLIC_LEMONSQUEEZY_VARIANT_ID_ELITE || ""}
                                label="Upgrade Account"
                                className="w-full bg-blue-600 hover:bg-blue-500 text-white rounded-xl h-10 text-[10px] uppercase tracking-widest font-bold mt-4"
                            />
                        </div>
                    )}
                </div>

                {/* Ledger Section */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <h2 className="text-lg font-bold">Activity Ledger</h2>
                        <span className="text-[10px] text-zinc-600 font-mono uppercase tracking-widest">Last 20 operations</span>
                    </div>
                    <UsageLedger entries={ledger} />
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
