"use client";

import Link from "next/link";

export default function SecurityPage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
            {/* Header */}
            <header className="border-b border-slate-700/50 backdrop-blur-sm bg-slate-900/50 sticky top-0 z-50">
                <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
                    <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                        Side
                    </Link>
                    <nav className="flex items-center gap-6">
                        <Link href="/pricing" className="text-slate-300 hover:text-white transition">Pricing</Link>
                        <Link href="/login" className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg transition">
                            Get Started
                        </Link>
                    </nav>
                </div>
            </header>

            {/* Content */}
            <main className="max-w-4xl mx-auto px-6 py-16">
                {/* Hero */}
                <div className="text-center mb-16">
                    <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-full px-4 py-2 mb-6">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                        <span className="text-green-400 text-sm font-medium">Zero Retention Policy</span>
                    </div>
                    <h1 className="text-5xl font-bold mb-6">
                        Security & Trust
                    </h1>
                    <p className="text-xl text-slate-400 max-w-2xl mx-auto">
                        We never see, read, or store your code.
                    </p>
                </div>

                {/* Architecture */}
                <div className="bg-slate-800/50 rounded-2xl border border-slate-700/50 p-8 mb-12">
                    <h2 className="text-2xl font-bold mb-6 text-center">How It Works</h2>
                    <div className="font-mono text-sm text-slate-300 overflow-x-auto">
                        <pre className="text-center">
                            {`Your Machine          Side API           LLM
┌──────────┐         ┌──────────┐       ┌──────────┐
│ Side MCP │────────▶│ Stateless│──────▶│ Analysis │
│          │◀────────│ Proxy    │◀──────│          │
└──────────┘         └──────────┘       └──────────┘
    │                     │
    │                     │
 Reads your           Zero retention.
 local files.         We don't care
                      who you are.`}
                        </pre>
                    </div>
                </div>

                {/* What We Store */}
                <div className="grid md:grid-cols-2 gap-8 mb-12">
                    <div className="bg-red-500/10 rounded-2xl border border-red-500/20 p-6">
                        <h3 className="text-xl font-bold mb-4 text-red-400">❌ Never Stored</h3>
                        <ul className="space-y-3 text-slate-300">
                            <li className="flex items-center gap-3">
                                <span className="text-red-400">✕</span> Your source code
                            </li>
                            <li className="flex items-center gap-3">
                                <span className="text-red-400">✕</span> File paths
                            </li>
                            <li className="flex items-center gap-3">
                                <span className="text-red-400">✕</span> Git history
                            </li>
                            <li className="flex items-center gap-3">
                                <span className="text-red-400">✕</span> Secrets & credentials
                            </li>
                        </ul>
                    </div>

                    <div className="bg-green-500/10 rounded-2xl border border-green-500/20 p-6">
                        <h3 className="text-xl font-bold mb-4 text-green-400">✅ Only Stored</h3>
                        <ul className="space-y-3 text-slate-300">
                            <li className="flex items-center gap-3">
                                <span className="text-green-400">✓</span> Your email (for account)
                            </li>
                            <li className="flex items-center gap-3">
                                <span className="text-green-400">✓</span> Token usage (for billing)
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Compliance */}
                <div className="bg-slate-800/50 rounded-2xl border border-slate-700/50 p-8 mb-12">
                    <h2 className="text-2xl font-bold mb-6 text-center">Compliance</h2>
                    <div className="grid md:grid-cols-3 gap-6">
                        <div className="text-center">
                            <div className="text-3xl mb-2">🛡️</div>
                            <div className="font-bold text-green-400">GDPR</div>
                            <div className="text-sm text-slate-400">Compliant</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl mb-2">📋</div>
                            <div className="font-bold text-blue-400">SOC 2</div>
                            <div className="text-sm text-slate-400">Planned</div>
                        </div>
                        <div className="text-center">
                            <div className="text-3xl mb-2">🔐</div>
                            <div className="font-bold text-purple-400">ISO 27001</div>
                            <div className="text-sm text-slate-400">Planned</div>
                        </div>
                    </div>
                </div>

                {/* Contact */}
                <div className="text-center">
                    <h2 className="text-2xl font-bold mb-4">Report a Vulnerability</h2>
                    <p className="text-slate-400 mb-6">
                        We respond within 24 hours.
                    </p>
                    <a href="mailto:security@side.ai" className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-500 px-6 py-3 rounded-lg transition font-medium">
                        security@side.ai
                    </a>
                </div>
            </main>

            {/* Footer */}
            <footer className="border-t border-slate-700/50 py-8 mt-16">
                <div className="max-w-6xl mx-auto px-6 flex items-center justify-between text-slate-400 text-sm">
                    <span>© 2026 Side AI. All rights reserved.</span>
                    <div className="flex gap-6">
                        <Link href="/privacy" className="hover:text-white transition">Privacy</Link>
                        <Link href="/terms" className="hover:text-white transition">Terms</Link>
                        <Link href="/security" className="hover:text-white transition">Security</Link>
                    </div>
                </div>
            </footer>
        </div>
    );
}
