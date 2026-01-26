"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

const commands = [
    // Scenario 1: The Secret Sniffer (Security)
    { cmd: "sidelith watch .", output: "🔭 Watcher Active: /src/payments" },
    { cmd: "", output: "   [09:14:22] 🔎 Analyzing src/payments/stripe.py..." },
    { cmd: "", output: "   [09:14:23] 🚨 CRITICAL (SEC-002): High Entropy String Detected" },
    { cmd: "", output: "   >> 'sk_live_51M...' (Likelihood: 99.8%)" },
    { cmd: "", output: "   >> Action: BLOCKED commit. Scrubbing required." },

    // Scenario 2: The Shadow Import (Integrity)
    { cmd: "git commit -m 'fix auth'", output: "   [09:15:10] ⚡️ AST Pre-Flight Check..." },
    { cmd: "", output: "   [09:15:11] ❌ ERROR (INT-005): Shadow Import Detected" },
    { cmd: "", output: "   >> You imported 'auth_v1' (Deprecated in ARCHITECTURE.md)" },
    { cmd: "", output: "   >> Context: 'auth_v2' is required for strict-mode." },

    // Scenario 3: The Amnesia Check (Registry)
    { cmd: "side query 'Why Postgres?'", output: "   [09:16:05] 🧠 Querying Sovereign Registry..." },
    { cmd: "", output: "   >> FACT: Switched to Postgres on Jan 12 (Commit a7f2)" },
    { cmd: "", output: "   >> REASON: 'SQLite lock contention during bulk writes'" },
    { cmd: "", output: "   >> SOURCE: MONOLITH.md (Line 450)" },
];

export function TerminalDemo() {
    const [lineIndex, setLineIndex] = useState(0);

    useEffect(() => {
        const timer = setInterval(() => {
            setLineIndex((prev) => (prev + 1) % (commands.length + 4)); // Pause at end
        }, 1500);
        return () => clearInterval(timer);
    }, []);

    return (
        <div className="w-full max-w-lg mx-auto overflow-hidden rounded-lg border border-white/10 bg-[#0A0A0A] shadow-2xl font-mono text-sm leading-relaxed">
            <div className="flex items-center gap-1.5 px-4 py-3 bg-white/5 border-b border-white/5">
                <div className="w-2.5 h-2.5 rounded-full bg-red-500/50" />
                <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/50" />
                <div className="w-2.5 h-2.5 rounded-full bg-green-500/50" />
                <div className="ml-auto text-[10px] text-zinc-600 font-bold uppercase tracking-widest">zsh — 80x24</div>
            </div>
            <div className="p-6 h-[300px] flex flex-col justify-end text-zinc-300">
                {commands.map((step, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: lineIndex > i ? 1 : 0, y: lineIndex > i ? 0 : 10 }}
                        className="mb-4"
                    >
                        <div className="flex gap-2 text-emerald-500">
                            <span>➜</span>
                            <span className="text-white">{step.cmd}</span>
                        </div>
                        <div className="text-zinc-500 pl-4 mt-1">{step.output}</div>
                    </motion.div>
                ))}
                <div className="flex gap-2">
                    <span className="text-emerald-500">➜</span>
                    <motion.div
                        animate={{ opacity: [0, 1, 0] }}
                        transition={{ repeat: Infinity, duration: 0.8 }}
                        className="w-2 h-5 bg-white/50"
                    />
                </div>
            </div>
        </div>
    );
}
