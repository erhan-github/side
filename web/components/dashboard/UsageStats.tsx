"use client";

import { TrendingUp, BarChart3, ArrowUpRight } from "lucide-react";

// Simplified Visual-Only Chart (to avoid heavy recharts dependency for now)
export function UsageStats() {
    const data = [12, 18, 10, 24, 32, 28, 45]; // Activity units
    const max = Math.max(...data);

    return (
        <div className="bg-[#0c0c0e] border border-white/10 rounded-xl p-5 flex flex-col h-full bg-[linear-gradient(45deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[length:10px_10px]">
            {/* Header */}
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-sm font-medium text-white flex items-center gap-2">
                        <BarChart3 className="w-4 h-4 text-zinc-500" /> Usage Stats
                    </h3>
                    <p className="text-xs text-zinc-500 mt-0.5">System Activity (7d)</p>
                </div>
                <div className="text-xl font-bold text-white font-mono tracking-tight flex items-baseline gap-1">
                    Active <span className="text-emerald-500 text-[10px] font-sans animate-pulse">●</span>
                </div>
            </div>

            {/* Chart Visualization - Flexible Height */}
            <div className="flex-1 flex items-end gap-2 pl-2 pb-2 border-l border-b border-white/10 relative min-h-[100px]">
                {data.map((val, i) => {
                    const height = (val / max) * 100;
                    return (
                        <div key={i} className="flex-1 group relative h-full flex items-end">
                            {/* Bar */}
                            <div
                                className="w-full bg-zinc-800/50 hover:bg-blue-500 transition-colors duration-300 rounded-t-[1px] relative cursor-crosshair backdrop-blur-sm group-hover:shadow-[0_0_10px_rgba(59,130,246,0.5)]"
                                style={{ height: `${height}%` }}
                            >
                                <div className="absolute top-0 w-full h-[1px] bg-white/20" />
                            </div>
                        </div>
                    )
                })}
            </div>

            {/* Legend */}
            <div className="flex justify-between mt-2 text-[10px] text-zinc-600 font-mono uppercase tracking-widest">
                <span>Mon</span>
                <span>Sun</span>
            </div>

            {/* Insight */}
            <div className="mt-3 p-2.5 bg-blue-500/5 border border-blue-500/10 rounded-lg flex gap-2.5 text-xs leading-relaxed items-start">
                <div className="min-w-5 min-h-5 bg-blue-500/10 rounded-md flex items-center justify-center mt-0.5">
                    <TrendingUp className="w-3 h-3 text-blue-400" />
                </div>
                <p className="text-zinc-400 text-[11px]">
                    <span className="text-blue-300 font-bold">Activity Trend:</span> Your project's semantic velocity is increasing.
                </p>
            </div>
        </div>
    );
}
