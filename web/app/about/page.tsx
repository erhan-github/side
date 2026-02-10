import { Mail, Github } from "lucide-react";

export const metadata = {
    title: "About - Sidelith",
    description: "Sidelith gives AI coding tools persistent memory of your codebase.",
};

export default function AboutPage() {
    return (
        <main className="min-h-screen bg-void text-foreground pt-40 pb-20">
            <div className="max-w-7xl mx-auto px-6">
                <div className="max-w-3xl">
                    {/* Header */}
                    <div className="mb-12">
                        <h1 className="text-4xl font-extrabold text-white mb-6 tracking-tight">About Sidelith</h1>
                        <p className="text-xl text-zinc-300 leading-relaxed">
                            We give AI coding tools memory of your codebase.
                        </p>
                    </div>

                    {/* The Problem */}
                    <section className="mb-12">
                        <h2 className="text-2xl font-bold text-white mb-6">The Problem</h2>
                        <div className="space-y-4 text-zinc-400 leading-relaxed text-lg">
                            <p>
                                AI coding assistants are powerful—but they forget everything between sessions.
                            </p>
                            <p>
                                Every conversation starts from zero. You re-explain your architecture.
                                You repeat your patterns. You watch AI suggest code that breaks your conventions.
                            </p>
                            <p className="text-white">
                                We built Sidelith to fix this.
                            </p>
                        </div>
                    </section>

                    {/* What We Built */}
                    <section className="mb-16">
                        <h2 className="text-2xl font-bold text-white mb-6">What We Built</h2>
                        <div className="grid gap-6">
                            <div className="p-6 rounded-xl bg-white/[0.02] border border-white/5">
                                <h3 className="text-lg font-bold text-white mb-3">Code Structure Indexing</h3>
                                <p className="text-zinc-400 leading-relaxed">
                                    Sidelith indexes your project structure using Tree-sitter AST parsing.
                                    Your code stays on your machine. The index lives in <code className="text-emerald-400">.side/</code> directory.
                                </p>
                            </div>

                            <div className="p-6 rounded-xl bg-white/[0.02] border border-white/5">
                                <h3 className="text-lg font-bold text-white mb-3">AI Memory Injection</h3>
                                <p className="text-zinc-400 leading-relaxed">
                                    When you use Cursor or VS Code, Sidelith injects your project context via
                                    the Model Context Protocol (MCP). AI sees your actual folder structure and patterns.
                                </p>
                            </div>

                            <div className="p-6 rounded-xl bg-white/[0.02] border border-white/5">
                                <h3 className="text-lg font-bold text-white mb-3">Works Everywhere</h3>
                                <p className="text-zinc-400 leading-relaxed">
                                    Compatible with Cursor, VS Code, Claude Desktop, Windsurf, and any MCP-enabled tool.
                                    Install once, works across all your AI assistants.
                                </p>
                            </div>
                        </div>
                    </section>

                    {/* How It Helps */}
                    <section className="mb-16">
                        <h2 className="text-2xl font-bold text-white mb-6">How It Helps</h2>
                        <div className="p-8 rounded-xl bg-white/[0.02] border border-white/10">
                            <div className="space-y-6">
                                <div>
                                    <h3 className="text-white font-semibold mb-2">Before Sidelith:</h3>
                                    <ul className="text-zinc-400 space-y-2">
                                        <li>• AI suggests files in wrong locations</li>
                                        <li>• You explain your architecture every session</li>
                                        <li>• Code suggestions break your patterns</li>
                                        <li>• Context is lost between conversations</li>
                                    </ul>
                                </div>
                                <div>
                                    <h3 className="text-white font-semibold mb-2">After Sidelith:</h3>
                                    <ul className="text-emerald-400 space-y-2">
                                        <li>• AI knows your folder structure</li>
                                        <li>• Suggestions match your conventions</li>
                                        <li>• Context persists across sessions</li>
                                        <li>• Less explaining, more building</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* Our Approach */}
                    <section className="mb-16">
                        <h2 className="text-2xl font-bold text-white mb-6">Our Approach</h2>
                        <div className="space-y-4 text-zinc-400 leading-relaxed text-lg">
                            <p>
                                <strong className="text-white">Local-first.</strong> Your code never leaves your machine.
                                All indexing happens locally.
                            </p>
                            <p>
                                <strong className="text-white">Privacy-focused.</strong> We index structure and patterns,
                                not file contents. No code is uploaded to our servers.
                            </p>
                            <p>
                                <strong className="text-white">Open standards.</strong> Built on MCP, works with any
                                compatible tool. No vendor lock-in.
                            </p>
                        </div>
                    </section>

                    {/* Team */}
                    <section className="mb-16">
                        <h2 className="text-2xl font-bold text-white mb-6">Who We Are</h2>
                        <p className="text-zinc-400 leading-relaxed text-lg">
                            We're developers who got tired of re-explaining our codebases to AI.
                            So we built the tool we wanted to use.
                        </p>
                    </section>

                    {/* Contact */}
                    <section>
                        <h2 className="text-2xl font-bold text-white mb-6">Get in Touch</h2>
                        <div className="grid md:grid-cols-2 gap-6">
                            <a
                                href="mailto:hello@sidelith.com"
                                className="p-6 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all group"
                            >
                                <div className="flex items-center gap-3 mb-3">
                                    <Mail className="text-emerald-500" size={24} />
                                    <h3 className="text-lg font-bold text-white group-hover:text-emerald-500 transition-colors">
                                        Email
                                    </h3>
                                </div>
                                <p className="text-zinc-400">hello@sidelith.com</p>
                            </a>

                            <a
                                href="https://github.com/sidelith"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="p-6 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all group"
                            >
                                <div className="flex items-center gap-3 mb-3">
                                    <Github className="text-blue-500" size={24} />
                                    <h3 className="text-lg font-bold text-white group-hover:text-blue-500 transition-colors">
                                        GitHub
                                    </h3>
                                </div>
                                <p className="text-zinc-400">See our open-source work</p>
                            </a>
                        </div>
                    </section>
                </div>
            </div>
        </main>
    );
}
