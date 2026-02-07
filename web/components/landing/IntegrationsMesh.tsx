import { Terminal, Cpu, Globe, Database } from "lucide-react";

export function IntegrationsMesh() {
    return (
        <section className="section-spacing w-full max-w-6xl px-6 py-20">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
                <div>
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">Integrate <span className="text-amber-500">Everywhere</span>.</h2>
                    <p className="text-white/40 text-lg font-light leading-relaxed mb-8">
                        Sidelith lives where you code. From your terminal to your preferred AI IDE, we provide a unified semantic bridge.
                    </p>
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 flex items-center gap-3">
                            <Terminal size={20} className="text-white/40" />
                            <span className="text-xs font-bold text-white/60">CLI</span>
                        </div>
                        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 flex items-center gap-3">
                            <Cpu size={20} className="text-white/40" />
                            <span className="text-xs font-bold text-white/60">Cursor</span>
                        </div>
                        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 flex items-center gap-3">
                            <Globe size={20} className="text-white/40" />
                            <span className="text-xs font-bold text-white/60">VS Code</span>
                        </div>
                        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 flex items-center gap-3">
                            <Database size={20} className="text-white/40" />
                            <span className="text-xs font-bold text-white/60">JetBrains</span>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="md:col-span-2 p-6 rounded-[28px] bg-[#0a0a0a] border border-white/5 hover:border-emerald-500/30 transition-all group">
                        <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center mb-4 border border-emerald-500/20">
                            <Cpu size={20} className="text-emerald-500" />
                        </div>
                        <h4 className="text-lg font-bold text-white mb-2">Terminal</h4>
                        <p className="text-white/40 text-xs mb-3">Direct CLI Access</p>
                        <div className="text-[8px] font-mono text-emerald-500/60 uppercase tracking-widest">SIDE_CLI</div>
                    </div>
                </div>
            </div>
        </section>
    );
}
