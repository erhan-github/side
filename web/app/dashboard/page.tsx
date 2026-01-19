import { Activity, CreditCard } from "lucide-react";
import Link from "next/link";
import { RefillButton } from "./refill-button";
import { supabase } from "@/lib/supabase";
import { ActivityLedger } from "@/components/activity-ledger";

export default async function Dashboard() {
    const { data: { user } } = await supabase.auth.getUser();
    const userId = user?.id || "mock_user";

    // Fetch real data from Local API
    let activities: any[] = [];
    let localProfile = { tier: 'free', balance: 50000 };

    const appUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';

    try {
        const [activityRes, profileRes] = await Promise.all([
            fetch(`${appUrl}/api/forensics?action=activities`, { cache: 'no-store' }),
            fetch(`${appUrl}/api/forensics?action=profile`, { cache: 'no-store' })
        ]);

        if (activityRes.ok) activities = await activityRes.json();
        if (profileRes.ok) localProfile = await profileRes.json();
    } catch (error) {
        console.error('Failed to fetch data:', error);
    }

    const tokenBalance = localProfile.balance;
    const userTier = localProfile.tier;
    const formattedTokens = new Intl.NumberFormat().format(tokenBalance);

    return (
        <div className="min-h-screen bg-black text-white selection:bg-white/20 font-sans tracking-tight">
            {/* Minimalist Sidebar */}
            <aside className="fixed left-0 top-0 bottom-0 w-64 border-r border-white/5 bg-black z-50">
                <div className="p-8">
                    <div className="flex items-center gap-3 mb-12">
                        <div className="h-5 w-5 bg-white rounded-[2px]" />
                        <span className="font-black text-lg tracking-tighter">SIDE <span className="text-zinc-500">MCP</span></span>
                    </div>

                    <nav className="flex flex-col gap-2">
                        <Link href="/dashboard" className="flex items-center gap-3 px-4 py-2 text-xs font-bold bg-white/5 text-white rounded-[4px] border border-white/5 shadow-inner">
                            <Activity className="w-3.5 h-3.5" />
                            ACTIVITY
                        </Link>
                        <Link href="/pricing" className="flex items-center gap-3 px-4 py-2 text-xs font-bold text-zinc-500 hover:text-zinc-200 transition-colors">
                            <CreditCard className="w-3.5 h-3.5" />
                            BILLING
                        </Link>
                    </nav>
                </div>

                {/* Token Balance (Cursor-style) */}
                <div className="absolute bottom-8 left-8 right-8">
                    <div className="p-5 rounded-lg border border-white/5 bg-zinc-900/30">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-[10px] font-mono text-zinc-600 uppercase tracking-widest">Balance</span>
                            <span className="text-[10px] font-bold text-blue-500 uppercase">{userTier} plan</span>
                        </div>
                        <div className="text-2xl font-black font-mono tracking-tighter mb-4">{formattedTokens}</div>
                        <RefillButton />
                    </div>
                </div>
            </aside>

            {/* Main Content - Cursor-style (Activity Log Only) */}
            <main className="pl-64">
                <header className="h-20 border-b border-white/5 flex items-center justify-between px-10 sticky top-0 bg-black/80 backdrop-blur-md z-40">
                    <div className="flex items-center gap-4">
                        <h1 className="text-xs font-bold tracking-[0.3em] text-zinc-500 uppercase">Activity Log</h1>
                        <div className="h-1 w-1 rounded-full bg-zinc-800" />
                        <span className="text-[10px] font-mono text-zinc-400">CURSOR-STYLE</span>
                    </div>
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2 text-[9px] text-zinc-500 font-mono tracking-widest">
                            <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                            SYSTEM READY
                        </div>
                        <div className="w-8 h-8 rounded-full bg-zinc-900 border border-white/5" />
                    </div>
                </header>

                {/* Activity Log (Full Width) */}
                <div className="p-10 max-w-4xl">
                    <ActivityLedger activities={activities} />
                </div>
            </main>
        </div>
    );
}
