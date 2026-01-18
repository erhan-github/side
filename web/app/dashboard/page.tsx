import { Zap, Activity, CreditCard, Shield, TrendingUp, GitCommit } from "lucide-react";
import Link from "next/link";
import { RefillButton } from "./refill-button";
import { supabase } from "@/lib/supabase";
import { PulseWidget } from "@/components/pulse-widget";
import { VisionGuard } from "@/components/vision-guard";
import { SanityAlert } from "@/components/sanity-alert";

export default async function Dashboard() {
    const { data: { user } } = await supabase.auth.getUser();
    const userId = user?.id || "mock_user";

    // 1. Fetch Profile & Decisions
    const { data: profile } = await supabase
        .from("profiles")
        .select("*")
        .eq("id", userId)
        .single();

    const { data: decisions } = await supabase
        .from("decisions")
        .select("*", { count: 'exact' })
        .eq("user_id", userId)
        .order("created_at", { ascending: false });

    const { data: goals } = await supabase
        .from("plans")
        .select("*")
        .eq("type", "goal");

    // 2. Fetch real Strategic IQ and Forensic Alerts from API
    let strategicIq = 100;
    let forensicAlerts: Array<{ type: string; severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'; message: string; action: string }> = [];

    try {
        // Fetch Strategic IQ
        const iqResponse = await fetch(`${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/api/forensics?action=iq`, {
            cache: 'no-store'
        });

        if (iqResponse.ok) {
            const iqData = await iqResponse.json();
            strategicIq = iqData.score || 100;
        }

        // Fetch Forensic Alerts
        const alertsResponse = await fetch(`${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/api/forensics?action=alerts`, {
            cache: 'no-store'
        });

        if (alertsResponse.ok) {
            forensicAlerts = await alertsResponse.json();
        }
    } catch (error) {
        console.error('Failed to fetch forensic data:', error);
        // Fall back to mock data
        forensicAlerts = [
            {
                type: 'SECURITY_PURITY',
                severity: 'CRITICAL',
                message: 'Supabase table creation detected without Row Level Security (RLS).',
                action: "Add 'ENABLE ROW LEVEL SECURITY' to migration."
            },
            {
                type: 'ARCH_PURITY',
                severity: 'HIGH',
                message: 'Redux detected in small project (< 20 components). Velocity Risk.',
                action: 'Downgrade to Zustand or Context.'
            }
        ];
    }

    // 3. Mock Pulse Signals (Extracting from recent decisions for now)
    const mockSignals = (decisions ?? []).slice(0, 3).map((d, i) => {
        const isToday = new Date(d.created_at).toDateString() === new Date().toDateString();
        return {
            type: (['SHORTCUT', 'MOAT', 'RISK'][i % 3]) as any,
            content: d.question.length > 60 ? d.question.substring(0, 57) + "..." : d.question,
            timestamp: isToday ? 'JUST NOW' : '2h ago'
        };
    });

    const tokenBalance = profile?.token_balance ?? 42850;
    const formattedTokens = new Intl.NumberFormat().format(tokenBalance);

    return (
        <div className="min-h-screen bg-black text-white selection:bg-white/20 font-sans">
            <aside className="fixed left-0 top-0 bottom-0 w-64 border-r border-white/10 bg-black/50 backdrop-blur-xl z-50">
                <div className="p-6">
                    <div className="flex items-center gap-2 mb-8">
                        <div className="h-6 w-6 bg-white rounded-sm" />
                        <span className="font-bold tracking-tight">CSO.ai</span>
                    </div>

                    <div className="flex flex-col gap-1">
                        <Link href="/dashboard" className="flex items-center gap-3 px-3 py-2 text-sm font-medium bg-white/10 text-white rounded-md text-glow">
                            <Activity className="w-4 h-4" />
                            Overview
                        </Link>
                        <Link href="/dashboard#decisions" className="flex items-center gap-3 px-3 py-2 text-sm font-medium text-zinc-400 hover:text-white rounded-md transition-shadow">
                            <Shield className="w-4 h-4" />
                            Decisions
                        </Link>
                        <Link href="/dashboard#strategy" className="flex items-center gap-3 px-3 py-2 text-sm font-medium text-zinc-400 hover:text-white rounded-md transition-shadow">
                            <TrendingUp className="w-4 h-4" />
                            Strategy
                        </Link>
                        <Link href="/pricing" className="flex items-center gap-3 px-3 py-2 text-sm font-medium text-zinc-400 hover:text-white rounded-md transition-shadow">
                            <CreditCard className="w-4 h-4" />
                            Billing
                        </Link>
                    </div>

                </div>

                <div className="absolute bottom-6 left-6 right-6">
                    <div className="p-4 rounded-lg bg-zinc-900 border border-white/10 shadow-2xl shadow-white/5">
                        <div className="text-xs text-zinc-500 mb-2 font-mono tracking-tighter uppercase">Token Reservoir</div>
                        <div className="text-2xl font-bold font-mono tracking-tight mb-1">{formattedTokens}</div>
                        <div className="w-full bg-zinc-800 h-1 rounded-full overflow-hidden mb-3">
                            <div
                                className="bg-gradient-to-r from-blue-500 to-white h-full transition-all duration-1000"
                                style={{ width: `${Math.min(100, (tokenBalance / 50000) * 100)}%` }}
                            />
                        </div>
                        <RefillButton />
                    </div>
                </div>
            </aside>

            <main className="pl-64">
                <header className="h-16 border-b border-white/10 flex items-center justify-between px-8 bg-black/50 backdrop-blur-sm sticky top-0 z-40">
                    <div className="flex items-center gap-4">
                        <h1 className="font-bold tracking-tight text-white/90">STRATEGIC HUB</h1>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-white/5 border border-white/10 text-zinc-500 uppercase tracking-widest">
                            v3.0.1
                        </span>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2 text-[10px] text-zinc-500 font-mono bg-zinc-900 px-3 py-1 rounded-full border border-white/5">
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
                            ENGINE ONLINE
                        </div>
                        <div className="w-8 h-8 bg-zinc-800 rounded-full border border-white/10 hover:border-white/30 transition-colors cursor-pointer" />
                    </div>
                </header>

                <div className="p-8 max-w-7xl mx-auto">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        <div className="p-1 rounded-2xl bg-gradient-to-br from-white/10 to-transparent">
                            <div className="h-full p-6 rounded-2xl bg-black/40 backdrop-blur-md">
                                <div className="flex items-center justify-between mb-4">
                                    <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">Strategic IQ</span>
                                    <Zap className="w-4 h-4 text-blue-400" />
                                </div>
                                <div className="text-4xl font-black font-mono tracking-tighter">
                                    {strategicIq}
                                    <span className="text-xs text-zinc-600 ml-1">V3</span>
                                </div>
                                <div className="text-[10px] text-blue-400/80 mt-2 font-bold uppercase tracking-widest">
                                    {strategicIq > 140 ? 'Geni-tier alignment' : 'Building Momentum'}
                                </div>
                            </div>
                        </div>

                        <div className="p-1 rounded-2xl bg-zinc-900 border border-white/5">
                            <div className="h-full p-6 bg-zinc-900/50 rounded-2xl">
                                <div className="flex items-center justify-between mb-4">
                                    <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">Market Moat</span>
                                    <Shield className="w-4 h-4 text-zinc-500" />
                                </div>
                                <div className="text-4xl font-black font-mono tracking-tighter">85%</div>
                                <div className="text-[10px] text-zinc-500 mt-2 font-bold uppercase tracking-widest">
                                    Defensive Core Solid
                                </div>
                            </div>
                        </div>

                        <div className="p-1 rounded-2xl bg-zinc-900 border border-white/5">
                            <div className="h-full p-6 bg-zinc-900/50 rounded-2xl">
                                <div className="flex items-center justify-between mb-4">
                                    <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">Velocity</span>
                                    <TrendingUp className="w-4 h-4 text-green-400" />
                                </div>
                                <div className="text-4xl font-black font-mono tracking-tighter">12<span className="text-xs text-zinc-600">pts/wk</span></div>
                                <div className="text-[10px] text-green-400 mt-2 font-bold uppercase tracking-widest">
                                    Accelerating
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
                        <PulseWidget signals={mockSignals} />
                        <VisionGuard status={{
                            alignmentScore: 92,
                            activeGoals: goals?.length || 0,
                            driftsDetected: 0,
                            status: 'OPTIMAL'
                        }} />
                    </div>

                    <h2 className="text-sm font-bold uppercase tracking-[0.2em] text-zinc-500 mb-6 flex items-center gap-2">
                        <GitCommit className="w-4 h-4" />
                        Strategic Ledger
                    </h2>
                    <div className="border border-white/5 rounded-2xl bg-zinc-900/20 backdrop-blur-sm overflow-hidden shadow-2xl mb-12">
                        <table className="w-full text-sm text-left border-collapse">
                            <thead className="bg-white/5 border-b border-white/5">
                                <tr>
                                    <th className="px-6 py-4 font-mono text-[10px] text-zinc-500 uppercase tracking-widest">Inquiry</th>
                                    <th className="px-6 py-4 font-mono text-[10px] text-zinc-500 uppercase tracking-widest">Leverage</th>
                                    <th className="px-6 py-4 font-mono text-[10px] text-zinc-500 uppercase tracking-widest">Status</th>
                                    <th className="px-6 py-4 font-mono text-[10px] text-zinc-500 uppercase tracking-widest text-right">Age</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {(decisions ?? []).length > 0 ? (
                                    decisions?.map((d: any) => (
                                        <tr key={d.id} className="hover:bg-white/[0.04] transition-all group cursor-pointer">
                                            <td className="px-6 py-4 font-medium max-w-md truncate group-hover:text-white transition-colors">
                                                {d.question}
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 text-[10px] font-bold uppercase tracking-tighter border border-white/5">
                                                    {d.type || 'Strategic'}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-1.5 text-blue-500/80 font-bold text-[10px] uppercase tracking-widest">
                                                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_6px_rgba(59,130,246,0.6)]" />
                                                    Locked
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-zinc-500 font-mono text-[10px] text-right">
                                                {new Date(d.created_at || Date.now()).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan={4} className="px-6 py-24 text-center text-zinc-600 font-medium italic tracking-tight">
                                            No strategic data ingested. Ready for deployment.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>

                    <h2 className="text-sm font-bold uppercase tracking-[0.2em] text-zinc-500 mb-6 flex items-center gap-2">
                        <Shield className="w-4 h-4 text-zinc-500" />
                        Sanity Guard (Forensic Mode)
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {forensicAlerts.length > 0 ? (
                            forensicAlerts.slice(0, 6).map((alert, idx) => (
                                <SanityAlert key={idx} issue={alert} />
                            ))
                        ) : (
                            <div className="col-span-2 p-12 text-center border border-white/5 rounded-xl bg-zinc-900/20">
                                <div className="text-4xl mb-4">✅</div>
                                <p className="text-zinc-400 font-medium">No active strategic alerts.</p>
                                <p className="text-zinc-600 text-sm mt-2">Your codebase is clean!</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}
