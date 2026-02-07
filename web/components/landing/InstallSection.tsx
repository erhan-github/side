import { InstallWidget } from "@/components/InstallWidget";

export function InstallSection() {
    return (
        <section id="install-widget" className="section-spacing w-full max-w-5xl px-6 mb-32 relative z-10">
            <div className="relative p-12 rounded-[32px] bg-gradient-to-br from-emerald-500/[0.05] to-blue-500/[0.05] border border-emerald-500/20 overflow-hidden">
                <div className="absolute top-0 left-1/4 w-64 h-64 bg-emerald-500/10 blur-[100px] rounded-full" />
                <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-blue-500/10 blur-[100px] rounded-full" />

                <div className="relative z-10">
                    <div className="text-center mb-12">
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
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-center">
                            <div className="text-2xl font-bold text-emerald-500 mb-1">177M/s</div>
                            <div className="text-[10px] text-white/40 uppercase tracking-wider">Match Speed</div>
                        </div>
                        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-center">
                            <div className="text-2xl font-bold text-emerald-500 mb-1">&lt;1ms</div>
                            <div className="text-[10px] text-white/40 uppercase tracking-wider">Pulse Latency</div>
                        </div>
                        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-center">
                            <div className="text-2xl font-bold text-emerald-500 mb-1">&lt;5ms</div>
                            <div className="text-[10px] text-white/40 uppercase tracking-wider">Context Load</div>
                        </div>
                        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-center">
                            <div className="text-2xl font-bold text-emerald-500 mb-1">&lt;1%</div>
                            <div className="text-[10px] text-white/40 uppercase tracking-wider">CPU Usage</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
