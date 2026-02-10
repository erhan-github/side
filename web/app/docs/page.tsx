import { Header } from "@/components/Header";
import { LandingFooter } from "@/components/landing/LandingFooter";
import { CodeBlock } from "@/components/docs/CodeBlock";
import { SuccessIndicator } from "@/components/docs/SuccessIndicator";

export const metadata = {
    title: "Get Started | Sidelith",
    description: "Install Sidelith and connect your AI tools in 2 minutes.",
};

export default function DocsPage() {
    return (
        <div className="min-h-screen bg-[#050505] text-white font-sans">
            <Header />

            <div className="max-w-7xl mx-auto px-6 pt-32 pb-32">
                <div className="max-w-3xl">

                    {/* Hero */}
                    <div className="mb-12">
                        <div className="text-sm text-zinc-500 mb-4 flex items-center gap-2">
                            <a href="/docs" className="hover:text-zinc-300 transition-colors">Docs</a>
                            <span className="text-zinc-700">/</span>
                            <span className="text-white">Get Started</span>
                        </div>
                        <h1 className="text-4xl font-extrabold mb-6 font-heading tracking-tight">
                            Get Started
                        </h1>
                        <p className="text-lg text-zinc-300 mb-4 leading-relaxed">
                            Give your AI tools memory in <strong className="text-white">2 minutes</strong>.
                        </p>
                        <p className="text-zinc-400 max-w-2xl leading-relaxed">
                            Sidelith makes Cursor and Claude remember your architecture,
                            so they stop suggesting code that breaks your patterns.
                        </p>
                    </div>

                    {/* Step 1: Install */}
                    <section className="mb-12">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center text-white font-bold text-base">
                                1
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white tracking-tight">Install Sidelith</h2>
                                <div className="text-xs text-zinc-500 mt-0.5">⏱️ 30 seconds</div>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <p className="text-zinc-400 leading-relaxed">
                                Run this in your terminal:
                            </p>

                            <CodeBlock code="curl -fsSL https://sidelith.com/install.sh | sh" />

                            <SuccessIndicator
                                title="Success looks like:"
                                description="✅ Sidelith v1.x.x installed successfully"
                            />

                            {/* Inline troubleshooting */}
                            <details className="mt-4 group">
                                <summary className="text-sm text-zinc-500 hover:text-zinc-300 cursor-pointer list-none flex items-center gap-2 transition-colors">
                                    <span className="transition-transform group-open:rotate-90">▶</span>
                                    Having trouble?
                                </summary>
                                <div className="mt-4 pl-4 border-l border-white/10 space-y-4 text-sm">
                                    <div>
                                        <div className="text-red-400 font-medium mb-1">
                                            ❌ "command not found: curl"
                                        </div>
                                        <div className="text-zinc-400 leading-relaxed">
                                            Install curl first:<br />
                                            • macOS: <code className="bg-zinc-800 px-2 py-1 rounded">brew install curl</code><br />
                                            • Ubuntu: <code className="bg-zinc-800 px-2 py-1 rounded">sudo apt install curl</code>
                                        </div>
                                    </div>
                                    <div>
                                        <div className="text-red-400 font-medium mb-1">
                                            ❌ "Permission denied"
                                        </div>
                                        <div className="text-zinc-400 leading-relaxed">
                                            Try with sudo: <code className="bg-zinc-800 px-2 py-1 rounded">curl ... | sudo sh</code>
                                        </div>
                                    </div>
                                </div>
                            </details>
                        </div>
                    </section>

                    {/* Step 2: Run Wizard */}
                    <section className="mb-12">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center text-white font-bold text-base">
                                2
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white tracking-tight">Run Setup</h2>
                                <div className="text-xs text-zinc-500 mt-0.5">⏱️ 1 minute</div>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <p className="text-zinc-400 leading-relaxed">
                                The wizard detects your AI tools and indexes your project automatically:
                            </p>

                            <CodeBlock code="side wizard" />

                            <div className="text-sm text-zinc-400">
                                <strong className="text-zinc-200">What happens:</strong>
                                <ul className="list-disc list-inside mt-2 space-y-1 ml-2">
                                    <li>Detects Cursor, VS Code, Claude Desktop</li>
                                    <li>Indexes your current project</li>
                                    <li>Configures everything automatically</li>
                                </ul>
                            </div>

                            <SuccessIndicator
                                title="Success looks like:"
                                description="✅ Setup complete! Indexed 142 files. Your AI tools now have context."
                            />
                        </div>
                    </section>

                    {/* Step 3: Verify */}
                    <section className="mb-12">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center text-white font-bold text-base">
                                3
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white tracking-tight">See It Working</h2>
                                <div className="text-xs text-zinc-500 mt-0.5">⏱️ 30 seconds</div>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <p className="text-zinc-400 leading-relaxed">
                                Open Cursor (or VS Code) and ask about your project:
                            </p>

                            <CodeBlock
                                code="What is the architecture of this project?"
                                language="text"
                                showPrompt={false}
                            />

                            <div className="grid md:grid-cols-2 gap-6 my-8">
                                <div className="p-6 rounded-xl border border-red-900/10 bg-red-950/10 backdrop-blur-sm">
                                    <div className="text-xs font-bold text-red-400 uppercase mb-3 tracking-widest">
                                        Before Sidelith
                                    </div>
                                    <div className="text-sm text-zinc-400 leading-relaxed">
                                        Generic response about common patterns.<br /><br />
                                        AI doesn't know YOUR specific project structure.
                                    </div>
                                </div>
                                <div className="p-6 rounded-xl border border-emerald-900/20 bg-emerald-950/10 backdrop-blur-sm">
                                    <div className="text-xs font-bold text-emerald-400 uppercase mb-3 tracking-widest">
                                        With Sidelith
                                    </div>
                                    <div className="text-sm text-zinc-200 leading-relaxed">
                                        Your project uses:<br />
                                        • React components in <code className="bg-zinc-800 px-1.5 rounded text-xs">src/components</code><br />
                                        • API routes in <code className="bg-zinc-800 px-1.5 rounded text-xs">src/api</code><br />
                                        • TypeScript strict mode
                                    </div>
                                </div>
                            </div>

                            <SuccessIndicator
                                title="It's working!"
                                description="If AI describes YOUR actual project structure, Sidelith is connected."
                            />
                        </div>
                    </section>

                    {/* Completion */}
                    <div className="pt-12 border-t border-white/10 mb-12">
                        <h2 className="text-3xl font-bold mb-4 tracking-tight">✅ You're All Set!</h2>
                        <p className="text-zinc-400 mb-8 max-w-2xl leading-relaxed">
                            Your AI tools now remember your codebase. Cursor knows your file structure,
                            Claude remembers your patterns, and AI suggestions match your style.
                        </p>
                    </div>

                    {/* What's Next */}
                    <div className="mb-20">
                        <h2 className="text-xl font-semibold mb-6 text-white tracking-tight">What's next?</h2>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <a
                                href="/docs/cli"
                                className="block p-4 rounded-lg border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] hover:border-emerald-500/30 transition-all group"
                            >
                                <div className="font-medium text-white group-hover:text-emerald-400 transition-colors">
                                    CLI Reference →
                                </div>
                                <div className="text-xs text-zinc-400 mt-1">
                                    All commands available in the Sidelith CLI
                                </div>
                            </a>

                            <a
                                href="/docs/how-it-works"
                                className="block p-4 rounded-lg border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] hover:border-emerald-500/30 transition-all group"
                            >
                                <div className="font-medium text-white group-hover:text-emerald-400 transition-colors">
                                    How it works →
                                </div>
                                <div className="text-xs text-zinc-400 mt-1">
                                    The Sidelith context engine explained
                                </div>
                            </a>
                        </div>

                        <div className="mt-4">
                            <a
                                href="/docs/glossary"
                                className="block p-4 rounded-lg border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] hover:border-emerald-500/30 transition-all group"
                            >
                                <div className="font-medium text-white group-hover:text-emerald-400 transition-colors">
                                    Terminology Glossary →
                                </div>
                                <div className="text-xs text-zinc-400 mt-1">
                                    Component definitions and naming conventions
                                </div>
                            </a>
                        </div>

                    </div>

                    {/* Help */}
                    <div className="pt-8 border-t border-white/10">
                        <p className="text-sm text-zinc-500 leading-relaxed">
                            Need help?{" "}
                            <a href="https://discord.gg/sidelith" className="text-emerald-400 hover:text-emerald-300 underline-offset-4 hover:underline">
                                Join Discord
                            </a>
                            ,{" "}
                            <a href="mailto:support@sidelith.com" className="text-emerald-400 hover:text-emerald-300 underline-offset-4 hover:underline">
                                email support
                            </a>
                            , or check the{" "}
                            <a href="/docs/troubleshooting" className="text-emerald-400 hover:text-emerald-300 underline-offset-4 hover:underline">
                                Troubleshooting Guide
                            </a>.
                        </p>
                    </div>
                </div>
            </div>

            <LandingFooter />
        </div>
    );
}
