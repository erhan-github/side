import { Mail, Github } from "lucide-react";

export const metadata = {
    title: "About - Sidelith",
    description: "Learn about Sidelith's mission to cure digital amnesia and build deterministic memory for AI agents.",
};

export default function AboutPage() {
    return (
        <main className="min-h-screen bg-void text-foreground pt-32 pb-20">
            <div className="max-w-4xl mx-auto px-6">
                {/* Header */}
                <div className="mb-16">
                    <h1 className="text-5xl font-bold text-white mb-4">About Sidelith</h1>
                    <p className="text-xl text-white/60">
                        Curing digital amnesia, one codebase at a time.
                    </p>
                </div>

                {/* Mission */}
                <section className="mb-16">
                    <h2 className="text-3xl font-bold text-white mb-6">Our Mission</h2>
                    <div className="space-y-4 text-lg text-white/60 leading-relaxed">
                        <p>
                            AI agents are brilliant—but they forget. Every conversation starts from zero. Every context window is a race against amnesia.
                        </p>
                        <p>
                            <strong className="text-white">Sidelith is the cure.</strong>
                        </p>
                        <p>
                            We're building the <strong className="text-emerald-500">deterministic memory substrate</strong> that sits between you and your AI tools. Not a replacement—a <strong className="text-white">force multiplier</strong>.
                        </p>
                    </div>
                </section>

                {/* What We're Building */}
                <section className="mb-16">
                    <h2 className="text-3xl font-bold text-white mb-6">What We're Building</h2>
                    <div className="grid gap-6">
                        <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5">
                            <h3 className="text-xl font-bold text-emerald-500 mb-3">Fractal Memory</h3>
                            <p className="text-white/60">
                                We index your codebase into a Merkle tree of understanding—every function, every pattern, every architectural decision. Cryptographically verifiable. Instantly retrievable.
                            </p>
                        </div>

                        <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5">
                            <h3 className="text-xl font-bold text-blue-500 mb-3">Sovereign Intelligence</h3>
                            <p className="text-white/60">
                                Your data stays local. Your secrets stay yours. We sync anonymized patterns across the network while keeping strategic intent locked down. Privacy by design.
                            </p>
                        </div>

                        <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5">
                            <h3 className="text-xl font-bold text-purple-500 mb-3">Universal Bridge</h3>
                            <p className="text-white/60">
                                Works with Cursor, Claude Desktop, VS Code, Windsurf, and any MCP-compatible tool. One source of truth. Zero vendor lock-in.
                            </p>
                        </div>
                    </div>
                </section>

                {/* Why It Matters */}
                <section className="mb-16">
                    <h2 className="text-3xl font-bold text-white mb-6">Why It Matters</h2>
                    <div className="p-8 rounded-2xl bg-gradient-to-br from-emerald-500/[0.05] to-blue-500/[0.05] border border-emerald-500/20">
                        <p className="text-lg text-white/70 leading-relaxed mb-4">
                            Every developer has felt it: explaining the same architecture to ChatGPT for the hundredth time. Watching Cursor re-index your repo on every restart. Losing context mid-refactor.
                        </p>
                        <p className="text-lg text-white/70 leading-relaxed">
                            <strong className="text-white">We're done with that.</strong> Sidelith remembers—so your AI can focus on creating, not re-learning.
                        </p>
                    </div>
                </section>

                {/* Contact */}
                <section>
                    <h2 className="text-3xl font-bold text-white mb-6">Get in Touch</h2>
                    <div className="grid md:grid-cols-2 gap-6">
                        <a
                            href="mailto:hello@sidelith.com"
                            className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all group"
                        >
                            <div className="flex items-center gap-3 mb-3">
                                <Mail className="text-emerald-500" size={24} />
                                <h3 className="text-xl font-bold text-white group-hover:text-emerald-500 transition-colors">
                                    Email Us
                                </h3>
                            </div>
                            <p className="text-white/60">hello@sidelith.com</p>
                        </a>

                        <a
                            href="https://github.com/sidelith"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all group"
                        >
                            <div className="flex items-center gap-3 mb-3">
                                <Github className="text-blue-500" size={24} />
                                <h3 className="text-xl font-bold text-white group-hover:text-blue-500 transition-colors">
                                    GitHub
                                </h3>
                            </div>
                            <p className="text-white/60">Follow our open-source work</p>
                        </a>
                    </div>
                </section>
            </div>
        </main>
    );
}
