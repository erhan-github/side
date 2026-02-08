"use client";

import { useState } from "react";
import { Terminal, Copy, Check, Command, Monitor, Box, Zap, Code, Wind, Bot, Sparkles, Cpu, Lock } from "lucide-react";

type Platform = "cursor" | "claude" | "vscode" | "windsurf" | "terminal" | "gemini";
type Tier = "hobby" | "pro" | "elite";

export function InstallWidget() {
    const [active, setActive] = useState<Platform>("cursor");
    const [tier, setTier] = useState<Tier>("hobby");
    const [subscribedTiers, setSubscribedTiers] = useState<Tier[]>(["hobby"]);
    const [isActivating, setIsActivating] = useState(false);
    const [copied, setCopied] = useState<{ type: "foundation" | "activation" | "gateway", status: boolean }>({ type: "foundation", status: false });

    const foundationCommand = tier === "hobby"
        ? "curl -fsSL https://sidelith.com/install.sh | sh"
        : `curl -fsSL https://sidelith.com/install.sh | sh -s --tier ${tier}`;

    const platforms = [
        { id: "cursor", label: "Cursor", icon: Monitor, color: "text-blue-400" },
        { id: "claude", label: "Claude Desktop", icon: Bot, color: "text-purple-400" },
        { id: "vscode", label: "VS Code", icon: Code, color: "text-indigo-400" },
        { id: "windsurf", label: "Windsurf", icon: Wind, color: "text-cyan-400" },
        { id: "terminal", label: "Terminal", icon: Terminal, color: "text-emerald-400" },
        { id: "gemini", label: "Gemini CLI", icon: Sparkles, color: "text-amber-400" },
    ];


    const handleTierSelection = (selectedTier: Tier) => {
        if (!subscribedTiers.includes(selectedTier)) {
            setTier(selectedTier);
            setIsActivating(true);
        } else {
            setTier(selectedTier);
            setIsActivating(false);
        }
    };

    const activateTier = () => {
        // [SIMULATION]: Mocking a successful Stripe/LemonSqueezy checkout
        setIsActivating(false);
        if (!subscribedTiers.includes(tier)) {
            setSubscribedTiers([...subscribedTiers, tier]);
        }
    };

    const copyToClipboard = (text: string, type: "foundation" | "activation" | "gateway") => {
        navigator.clipboard.writeText(text);
        setCopied({ type, status: true });
        setTimeout(() => setCopied({ type, status: false }), 2000);
    };

    return (
        <section className="w-full max-w-5xl mx-auto mb-32 px-6 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300">
            <div className="text-center mb-10">
                <h3 className="text-2xl font-heading text-white mb-2">The Genesis Handshake</h3>
                <p className="text-white/50 max-w-2xl mx-auto">One command. Total System Control. Your node automatically initializes your active tier to lock your identity and auto-patch your entire IDE mesh in a single shot.</p>
            </div>

            {/* TIER DISPLAY (Static, as it's auto-detected) */}
            <div className="flex justify-center gap-4 mb-8">
                {[
                    { id: "hobby", label: "Hobby", su: "500 SUs", price: "$0", color: "border-white/10" },
                    { id: "pro", label: "Pro", su: "5,000 SUs", price: "$20", color: "border-blue-500/30" },
                    { id: "elite", label: "Elite", su: "25,000 SUs", price: "$60", color: "border-amber-500/30" }
                ].map((t) => {
                    const isActive = tier === t.id;
                    return (
                        <div
                            key={t.id}
                            className={`flex flex-col items-center p-4 min-w-[120px] rounded-xl border transition-all duration-300 relative overflow-hidden ${isActive
                                ? `${t.color} bg-white/5 shadow-[0_0_20px_rgba(255,255,255,0.05)]`
                                : 'border-white/5 opacity-40 grayscale'}`}
                        >
                            <span className="text-[10px] uppercase tracking-widest font-bold mb-1 text-white/40">{t.label}</span>
                            <span className="text-lg font-bold text-white">{t.price}</span>
                            <span className="text-[10px] font-mono text-zinc-500 mt-1">{t.su}</span>
                        </div>
                    );
                })}
            </div>

            <div className="grid grid-cols-1 gap-6">
                {/* SINGLE STEP: GENESIS */}
                <div className="bg-[#0a0a0a]/50 border border-white/10 rounded-2xl p-8 backdrop-blur-xl shadow-2xl relative overflow-hidden group min-h-[400px]">

                    {/* SUBSCRIPTION GUARD OVERLAY */}
                    {isActivating && (
                        <div className="absolute inset-0 z-50 bg-black/80 backdrop-blur-md flex flex-col items-center justify-center p-8 text-center animate-in fade-in duration-300">
                            <div className="w-16 h-16 rounded-2xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 mb-6 font-bold shadow-[0_0_30px_rgba(59,130,246,0.2)]">
                                <Lock size={32} />
                            </div>
                            <h4 className="text-2xl font-bold text-white mb-2 uppercase tracking-widest">Pricing Activation Required</h4>
                            <p className="text-white/50 max-w-md mb-8">Your node is requesting <b>{tier.toUpperCase()}</b> tier. Support the Sidelith mission to unlock your premium Service Units (SUs) and high-dimension reasoning.</p>
                            <button
                                onClick={activateTier}
                                className="px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold text-lg transition-all shadow-xl shadow-blue-500/40 hover:scale-105 active:scale-95"
                            >
                                Activate {tier.toUpperCase()} Tier
                            </button>
                            <button
                                onClick={() => { setIsActivating(false); setTier("hobby"); }}
                                className="mt-4 text-xs text-white/30 hover:text-white transition-colors"
                            >
                                Back to Hobby
                            </button>
                        </div>
                    )}
                    <div className="absolute top-0 right-0 p-6 opacity-5 pointer-events-none group-hover:opacity-10 transition-opacity">
                        <Zap size={150} />
                    </div>

                    <div className="flex items-center gap-4 mb-8">
                        <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 font-bold border border-blue-500/30 text-lg group-hover:scale-110 transition-transform">⚡</div>
                        <div>
                            <h4 className="text-lg font-bold text-white uppercase tracking-widest">Run in your Project Root</h4>
                            <p className="text-sm text-white/40">Open your terminal in your <b>active project directory</b> and run the command. Sidelith will anchor your local DNA and bridge your entire IDE mesh in a single shot.</p>
                        </div>
                    </div>

                    <div className="relative flex items-center bg-black border border-white/20 rounded-xl p-6 font-mono text-lg shadow-inner transition-all hover:border-blue-500/30 group-hover:shadow-[0_0_30px_-10px_rgba(59,130,246,0.3)]">
                        <span className="mr-4 text-white/30 select-none">$</span>
                        <span className="flex-1 text-blue-400 font-bold tracking-tight">{foundationCommand}</span>

                        <button
                            onClick={() => copyToClipboard(foundationCommand, "foundation")}
                            className="p-3 rounded-lg hover:bg-white/10 text-white/40 hover:text-white transition-all active:scale-95"
                        >
                            {copied.type === "foundation" && copied.status ? <Check size={24} className="text-blue-400" /> : <Copy size={24} />}
                        </button>
                    </div>

                    {/* Magic Detection Indicators */}
                    <div className="mt-12">
                        <div className="flex items-center gap-2 text-[10px] text-white/30 uppercase tracking-[0.2em] mb-4 font-bold">
                            <Sparkles size={12} className="text-blue-400 animate-pulse" /> Automatic MCP Injection Locked
                        </div>
                        <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
                            {platforms.map((p) => {
                                const Icon = p.icon;
                                return (
                                    <div key={p.id} className="flex flex-col items-center gap-2 p-4 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-all hover:-translate-y-1">
                                        <Icon size={24} className={p.color} />
                                        <span className="text-[10px] text-white/40 font-medium uppercase w-full text-center leading-tight">{p.label}</span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    <div className="mt-12 py-6 border-t border-white/5 flex items-center justify-center gap-10 opacity-40 text-[10px] uppercase tracking-[0.2em] font-mono">
                        <div className="flex items-center gap-2"><Lock size={14} /> JIT Auth</div>
                        <div className="w-1 h-1 rounded-full bg-white/20" />
                        <div className="flex items-center gap-2"><Zap size={14} /> Global Patching</div>
                        <div className="w-1 h-1 rounded-full bg-white/20" />
                        <div className="flex items-center gap-2"><Box size={14} /> Bridge Active</div>
                    </div>
                </div>
            </div>
        </section>
    );
}
