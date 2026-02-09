import { InstallWidget } from "@/components/InstallWidget";

export function InstallSection() {
    return (
        <section id="install-widget" className="w-full max-w-5xl px-6 pt-4 pb-32 relative z-10">
            <div className="relative p-12 rounded-[32px] bg-gradient-to-br from-emerald-500/[0.05] to-blue-500/[0.05] border border-emerald-500/20 overflow-hidden">
                <div className="absolute top-0 left-1/4 w-64 h-64 bg-emerald-500/10 blur-[100px] rounded-full" />
                <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-blue-500/10 blur-[100px] rounded-full" />

                <div className="relative z-10">
                    <div className="text-center mb-16">
                        <div className="inline-block px-4 py-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 text-emerald-500 font-mono text-[10px] tracking-widest uppercase mb-6">
                            ⚡ The Developer's Shortcut
                        </div>
                        <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                            Ready to <span className="text-emerald-400">Deploy</span>
                        </h2>
                        <p className="text-lg text-white/60 max-w-2xl mx-auto">
                            You don't need a heavy account. You need a binary. Start building with local-first intelligence in seconds.
                        </p>
                    </div>

                    <div className="mb-12">
                        <InstallWidget />

                        <div className="mt-8 text-center max-w-2xl mx-auto">
                            <p className="text-white/60 text-sm mb-6">
                                Sidelith lives where you code. From your terminal to your preferred AI IDE, we provide a universal connector.
                            </p>
                            <div className="flex flex-wrap justify-center gap-2">
                                {[
                                    { name: "Automatic Context Injection", color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" },
                                    { name: "Cursor" },
                                    { name: "Claude Desktop" },
                                    { name: "VS Code" },
                                    { name: "Windsurf" },
                                    { name: "Terminal" },
                                    { name: "Gemini CLI" }
                                ].map((provider) => (
                                    <span key={provider.name} className={`px-3 py-1.5 rounded-lg border border-white/5 bg-white/[0.02] text-[10px] font-mono uppercase tracking-wider ${provider.color || "text-white/40"}`}>
                                        {provider.name}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-center">
                            <div className="text-xl font-bold text-emerald-500 mb-1">High-Velocity</div>
                            <div className="text-[10px] text-white/40 uppercase tracking-wider">Match Speed</div>
                        </div>
                        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-center">
                            <div className="text-xl font-bold text-emerald-500 mb-1">Real-Time</div>
                            <div className="text-[10px] text-white/40 uppercase tracking-wider">Pulse Latency</div>
                        </div>
                        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-center">
                            <div className="text-xl font-bold text-emerald-500 mb-1">Instant</div>
                            <div className="text-[10px] text-white/40 uppercase tracking-wider">Context Load</div>
                        </div>
                        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-center">
                            <div className="text-xl font-bold text-emerald-500 mb-1">Minimal</div>
                            <div className="text-[10px] text-white/40 uppercase tracking-wider">CPU Usage</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
