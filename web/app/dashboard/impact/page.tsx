"use client";

import { BarChart3, TrendingUp, Zap, ArrowUpRight, Brain, Clock, Code, Share2 } from "lucide-react";

export default function ImpactPage() {
    return (
        <div className="p-4 md:p-8 max-w-[1600px] mx-auto min-h-screen flex flex-col gap-8 mt-16 md:mt-0">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
                <div>
                    <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight mb-2 flex items-center gap-3">
                        <BarChart3 className="w-8 h-8 text-indigo-500" />
                        Strategic Impact
                    </h1>
                    <p className="text-zinc-500 max-w-xl">
                        Measuring the ROI of your System. Side tracks not just code written, but cognitive load reduced.
                    </p>
                </div>
                <button className="bg-white text-black hover:bg-zinc-200 px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors">
                    <Share2 className="w-4 h-4" /> Share Report
                </button>
            </div>

            {/* Hero Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-[#0c0c0e] border border-white/10 rounded-xl p-6 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Brain className="w-24 h-24 text-indigo-500" />
                    </div>
                    <h3 className="text-sm font-medium text-zinc-400 mb-4 flex items-center gap-2">
                        <Brain className="w-4 h-4 text-indigo-500" /> Cognitive Load Reduced
                    </h3>
                    <div className="text-4xl font-bold text-white mb-2">84<span className="text-lg text-zinc-600 font-normal">%</span></div>
                    <div className="text-sm text-emerald-400 flex items-center gap-1">
                        <ArrowUpRight className="w-3 h-3" /> +12% this week
                    </div>
                    <p className="text-xs text-zinc-500 mt-4 leading-relaxed max-w-[80%]">
                        Based on "Audit" vs "Plan" ratio. You are spending significantly less time reviewing basics.
                    </p>
                </div>

                <div className="bg-[#0c0c0e] border border-white/10 rounded-xl p-6 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Clock className="w-24 h-24 text-blue-500" />
                    </div>
                    <h3 className="text-sm font-medium text-zinc-400 mb-4 flex items-center gap-2">
                        <Clock className="w-4 h-4 text-blue-500" /> Manual Review Saved
                    </h3>
                    <div className="text-4xl font-bold text-white mb-2">169<span className="text-lg text-zinc-600 font-normal">hrs</span></div>
                    <div className="text-sm text-emerald-400 flex items-center gap-1">
                        <ArrowUpRight className="w-3 h-3" /> +24hrs this week
                    </div>
                    <p className="text-xs text-zinc-500 mt-4 leading-relaxed max-w-[80%]">
                        Estimated at 5 mins per captured "Audit" event that required no intervention.
                    </p>
                </div>

                <div className="bg-[#0c0c0e] border border-white/10 rounded-xl p-6 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Code className="w-24 h-24 text-purple-500" />
                    </div>
                    <h3 className="text-sm font-medium text-zinc-400 mb-4 flex items-center gap-2">
                        <Code className="w-4 h-4 text-purple-500" /> Leverage Ratio
                    </h3>
                    <div className="text-4xl font-bold text-white mb-2">12.5<span className="text-lg text-zinc-600 font-normal">x</span></div>
                    <div className="text-sm text-zinc-500 flex items-center gap-1">
                        Stable
                    </div>
                    <p className="text-xs text-zinc-500 mt-4 leading-relaxed max-w-[80%]">
                        You generate 12.5x more impactful code changes per hour than the industry average.
                    </p>
                </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[400px]">
                {/* Visual Chart Mockup */}
                <div className="bg-[#0c0c0e] border border-white/10 rounded-xl p-6 flex flex-col">
                    <h3 className="text-white font-medium mb-6">Efficiency Trend</h3>
                    <div className="flex-1 flex items-end gap-2 px-4 pb-4">
                        {[40, 65, 45, 70, 85, 60, 90, 75, 50, 80, 95, 88].map((h, i) => (
                            <div key={i} className="flex-1 bg-white/5 hover:bg-indigo-500/50 transition-colors rounded-t-sm relative group" style={{ height: `${h}%` }}>
                                <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-zinc-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                                    Day {i + 1}: {h}%
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="flex justify-between text-xs text-zinc-500 px-4 pt-2 border-t border-white/5 font-mono">
                        <span>Day 1</span>
                        <span>Day 12</span>
                    </div>
                </div>

                {/* Insight Feed */}
                <div className="bg-[#0c0c0e] border border-white/10 rounded-xl p-6 flex flex-col">
                    <h3 className="text-white font-medium mb-6 flex items-center justify-between">
                        Strategic Wins
                        <span className="text-xs bg-white/10 text-zinc-400 px-2 py-1 rounded border border-white/5">Last 7 Days</span>
                    </h3>
                    <div className="flex-1 overflow-y-auto pr-2 space-y-4 custom-scrollbar">
                        {[
                            { title: "Circular Dependency Resolved", desc: "Refactored side.utils to prevent import cycles.", impact: "High" },
                            { title: "Capacity System Implemented", desc: "Added Value Vault and billing bypass logic.", impact: "Critical" },
                            { title: "Security Harden", desc: "Moved to Docker-based isolated environment.", impact: "Medium" },
                            { title: "Polyglot AST Support", desc: "Added Tree-sitter for TypeScript support.", impact: "High" },
                            { title: "Dashboard Polish", desc: "UI responsiveness fixed for mobile/tablet.", impact: "Low" }
                        ].map((win, i) => (
                            <div key={i} className="p-4 bg-zinc-900/30 rounded-lg border border-white/5 hover:border-indigo-500/30 transition-colors">
                                <div className="flex justify-between items-start mb-1">
                                    <h4 className="text-sm font-medium text-white">{win.title}</h4>
                                    <span className={`text-[10px] px-1.5 py-0.5 rounded border ${win.impact === 'Critical' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                                        win.impact === 'High' ? 'bg-orange-500/10 text-orange-400 border-orange-500/20' :
                                            'bg-blue-500/10 text-blue-400 border-blue-500/20'
                                        }`}>{win.impact}</span>
                                </div>
                                <p className="text-xs text-zinc-500">{win.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
