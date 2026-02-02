"use client";

import { useState } from "react";
import { Terminal, Copy, Check, Command, Monitor, Box, Zap, Code, Wind, Bot } from "lucide-react";

type Platform = "terminal" | "cursor" | "windsurf" | "vscode" | "zed" | "jetbrains" | "claude";

export function InstallWidget() {
    const [active, setActive] = useState<Platform>("terminal");
    const [copied, setCopied] = useState(false);

    const command = "curl -fsSL sidelith.com/install | sh";

    const copyToClipboard = () => {
        navigator.clipboard.writeText(command);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const platforms = [
        { id: "terminal", label: "Terminal", icon: Terminal, color: "text-white" },
        { id: "cursor", label: "Cursor", icon: Monitor, color: "text-blue-400" },
        { id: "windsurf", label: "Windsurf", icon: Wind, color: "text-cyan-400" },
        { id: "claude", label: "Claude", icon: Bot, color: "text-orange-400" },
        { id: "vscode", label: "VS Code", icon: Code, color: "text-blue-500" },
        { id: "zed", label: "Zed", icon: Zap, color: "text-yellow-400" },
        { id: "jetbrains", label: "JetBrains", icon: Box, color: "text-purple-500" },
    ];

    const instructions: Record<Platform, string> = {
        terminal: "Run in any standard shell (zsh, bash). Supports Antigravity.",
        cursor: "Open Cursor Integrated Terminal (Ctrl+~).",
        windsurf: "Works with Cascade. Run in Windsurf Terminal.",
        claude: "MCP Native. Add output to `claude_desktop_config.json`.",
        vscode: "Open VS Code Terminal (Ctrl+~). Detects Extensions.",
        zed: "Open Zed Terminal. We install the semantic features.",
        jetbrains: "Works in IntelliJ/PyCharm Terminal. Plugin auto-detects.",
    };

    return (
        <section className="w-full max-w-4xl mx-auto mb-32 px-6 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300">
            <div className="text-center mb-10">
                <h3 className="text-2xl font-heading text-white mb-2">Ready to Deploy?</h3>
                <p className="text-white/50">Select your environment. We handle the rest.</p>
            </div>

            <div className="bg-[#0a0a0a]/50 border border-white/10 rounded-2xl p-2 backdrop-blur-xl shadow-2xl">
                {/* Tabs */}
                <div className="flex flex-wrap gap-2 mb-6 p-2 border-b border-white/5">
                    {platforms.map((p) => {
                        const Icon = p.icon;
                        const isActive = active === p.id;
                        return (
                            <button
                                key={p.id}
                                onClick={() => setActive(p.id as Platform)}
                                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${isActive
                                    ? "bg-white/10 text-white shadow-lg ring-1 ring-white/5"
                                    : "text-white/40 hover:text-white hover:bg-white/5"
                                    }`}
                            >
                                <Icon size={16} className={isActive ? p.color : "opacity-50"} />
                                {p.label}
                            </button>
                        );
                    })}
                </div>

                {/* Content */}
                <div className="px-4 pb-6">
                    <div className="flex items-center justify-between text-xs text-stockholm-blue mb-4 font-mono">
                        <span className="flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                            {instructions[active]}
                        </span>
                    </div>

                    <div className="group relative flex items-center bg-black border border-white/10 rounded-xl p-4 font-mono text-sm shadow-inner transition-colors hover:border-white/20">
                        <span className="mr-3 text-white/30 select-none">$</span>
                        <span className="flex-1 text-emerald-400 font-bold tracking-wide">{command}</span>

                        <button
                            onClick={copyToClipboard}
                            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg hover:bg-white/10 text-white/40 hover:text-white transition-all active:scale-95"
                        >
                            {copied ? <Check size={16} className="text-emerald-400" /> : <Copy size={16} />}
                        </button>
                    </div>

                    <div className="mt-4 flex items-center justify-center gap-6 opacity-40 text-[10px] uppercase tracking-widest font-mono">
                        <span className="flex items-center gap-1.5"><Terminal size={12} /> CLI Installed</span>
                        <span className="w-px h-3 bg-white/20" />
                        <span className="flex items-center gap-1.5"><Zap size={12} /> MCP Server Active</span>
                        <span className="w-px h-3 bg-white/20" />
                        <span className="flex items-center gap-1.5"><Box size={12} /> Extensions Linked</span>
                    </div>
                </div>
            </div>
        </section>
    );
}
