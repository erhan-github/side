"use client";

import { Activity, Zap, Shield, Search, Users } from "lucide-react";

interface ActivityItem {
    id: number;
    tool: string;
    action: string;
    cost_tokens: number;
    tier: string;
    created_at: string;
    payload: any;
}

export function ActivityLedger({ activities }: { activities: ActivityItem[] }) {
    return (
        <div className="flex flex-col gap-4">
            <h2 className="text-[10px] font-mono text-zinc-500 uppercase tracking-[0.3em] mb-2 flex items-center gap-2">
                <Activity className="w-3 h-3" />
                Live Activity Stream
            </h2>

            <div className="flex flex-col border border-white/5 rounded-lg bg-zinc-900/10 overflow-hidden divide-y divide-white/5">
                {activities.length > 0 ? (
                    activities.map((activity) => (
                        <div key={activity.id} className="p-4 flex items-start justify-between hover:bg-white/[0.02] transition-colors group">
                            <div className="flex items-start gap-4">
                                <ActivityIcon tool={activity.tool} />
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="text-sm font-medium text-white/90 group-hover:text-white transition-colors">
                                            {activity.action}
                                        </span>
                                        <span className={`px-1.5 py-0.5 rounded-[4px] text-[8px] font-bold uppercase tracking-tighter border ${activity.tier === 'pro' || activity.tier === 'enterprise'
                                            ? 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                                            : 'bg-zinc-800 text-zinc-500 border-white/5'
                                            }`}>
                                            {activity.tier}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-3 text-[10px] text-zinc-500 font-mono">
                                        <span>{new Date(activity.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
                                        <span>•</span>
                                        <span className="text-zinc-400">{activity.tool.toUpperCase()}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="text-right flex flex-col items-end">
                                <div className="text-[10px] font-mono text-zinc-400 mb-1">
                                    {activity.cost_tokens > 0 ? `-${activity.cost_tokens}` : 'FREE'}
                                    <span className="text-zinc-600 ml-1">TKNS</span>
                                </div>
                                <div className="text-[8px] text-zinc-600 uppercase tracking-widest font-bold">
                                    DEBITED
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="p-12 text-center text-zinc-600 text-sm italic font-mono">
                        No operations logged. Use CLI or Tools to trigger scans.
                    </div>
                )}
            </div>
        </div>
    );
}

function ActivityIcon({ tool }: { tool: string }) {
    switch (tool.toLowerCase()) {
        case 'audit':
            return <div className="p-2 rounded bg-blue-500/10 text-blue-400 border border-blue-500/10"><Search className="w-4 h-4" /></div>;
        case 'simulate':
            return <div className="p-2 rounded bg-purple-500/10 text-purple-400 border border-purple-500/10"><Users className="w-4 h-4" /></div>;
        case 'decide':
        case 'strategy':
            return <div className="p-2 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/10"><Zap className="w-4 h-4" /></div>;
        default:
            return <div className="p-2 rounded bg-zinc-800 text-zinc-500 border border-white/5"><Shield className="w-4 h-4" /></div>;
    }
}
