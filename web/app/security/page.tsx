"use client";

import Link from "next/link";

export default function SecurityPage() {
    return (
        <div className="min-h-screen bg-black text-white">
            <div className="max-w-4xl mx-auto px-6 py-24">
                {/* Hero */}
                <div className="text-center mb-16">
                    <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-full px-4 py-2 mb-6">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                        <span className="text-green-400 text-sm font-medium">Local-First Architecture</span>
                    </div>
                    <h1 className="text-5xl font-bold mb-6">Security</h1>
                    <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
                        Your code never leaves your machine.
                    </p>
                </div>

                {/* Architecture */}
                <div className="bg-zinc-900 rounded-2xl border border-zinc-800 p-8 mb-12">
                    <h2 className="text-2xl font-bold mb-6 text-center">How It Works</h2>
                    <div className="font-mono text-sm text-zinc-300 overflow-x-auto">
                        <pre className="text-center whitespace-pre">
                            {`Your Machine        Sidelith API         AI Tool
┌──────────┐        ┌──────────┐        ┌──────────┐
│ MCP      │───────▶│ Stateless│───────▶│ Cursor/  │
│ Server   │◀───────│ Router   │◀───────│ VS Code  │
└──────────┘        └──────────┘        └──────────┘
     │                    │
     │                    │
 Reads your          Zero retention
 local index         Zero code storage`}
                        </pre>
                    </div>
                </div>

                {/* What We Store */}
                <div className="grid md:grid-cols-2 gap-8 mb-12">
                    <div className="bg-red-500/5 rounded-2xl border border-red-500/20 p-6">
                        <h3 className="text-xl font-bold mb-4 text-red-400">Never Stored</h3>
                        <ul className="space-y-3 text-zinc-300">
                            <li className="flex items-center gap-3">
                                <span className="text-red-400">✕</span> Source code
                            </li>
                            <li className="flex items-center gap-3">
                                <span className="text-red-400">✕</span> File paths
                            </li>
                            <li className="flex items-center gap-3">
                                <span className="text-red-400">✕</span> Git history
                            </li>
                            <li className="flex items-center gap-3">
                                <span className="text-red-400">✕</span> Secrets or credentials
                            </li>
                        </ul>
                    </div>

                    <div className="bg-green-500/5 rounded-2xl border border-green-500/20 p-6">
                        <h3 className="text-xl font-bold mb-4 text-green-400">Only Stored</h3>
                        <ul className="space-y-3 text-zinc-300">
                            <li className="flex items-center gap-3">
                                <span className="text-green-400">✓</span> Email (for authentication)
                            </li>
                            <li className="flex items-center gap-3">
                                <span className="text-green-400">✓</span> Usage metrics (for billing)
                            </li>
                            <li className="flex items-center gap-3">
                                <span className="text-green-400">✓</span> Project IDs (anonymized hashes)
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Compliance */}
                <div className="bg-zinc-900 rounded-2xl border border-zinc-800 p-8 mb-12">
                    <h2 className="text-2xl font-bold mb-6 text-center">Compliance</h2>
                    <div className="grid md:grid-cols-3 gap-6">
                        <div className="text-center">
                            <div className="text-3xl mb-2">🛡️</div>
                            <div className="font-bold text-green-400">GDPR</div>
                            <div className="text-sm text-zinc-400">Compliant</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl mb-2">📋</div>
                            <div className="font-bold text-blue-400">SOC 2</div>
                            <div className="text-sm text-zinc-400">In Progress</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl mb-2">🔐</div>
                            <div className="font-bold text-purple-400">ISO 27001</div>
                            <div className="text-sm text-zinc-400">Planned</div>
                        </div>
                    </div>
                </div>

                {/* Contact */}
                <div className="text-center bg-zinc-900 rounded-2xl border border-zinc-800 p-8">
                    <h2 className="text-2xl font-bold mb-4">Report a Vulnerability</h2>
                    <p className="text-zinc-400 mb-6">
                        Found a security issue? We respond within 24 hours.
                    </p>
                    <a
                        href="mailto:security@sidelith.com"
                        className="inline-flex items-center gap-2 bg-white text-black px-6 py-3 rounded-full font-medium hover:bg-zinc-200 transition"
                    >
                        security@sidelith.com
                    </a>
                </div>
            </div>
        </div>
    );
}
