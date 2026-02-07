import { Shield, Lock, Eye, Zap } from "lucide-react";

export function DefensiveMoats() {
    return (
        <section className="section-spacing w-full max-w-6xl px-6 py-32 relative overflow-hidden">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-blue-500/5 blur-[120px] rounded-full -z-10" />

            <div className="text-center mb-24">
                <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                    Defensive <span className="text-blue-400">Moats</span>.
                </h2>
                <p className="text-white/40 text-lg md:text-xl font-light">Built for the air-gapped technician.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="p-8 rounded-[32px] bg-[#0a0a0a] border border-white/5 hover:border-blue-500/20 transition-all group">
                    <div className="w-12 h-12 rounded-2xl bg-blue-500/10 flex items-center justify-center mb-6 border border-blue-500/20">
                        <Shield size={24} className="text-blue-500" />
                    </div>
                    <h4 className="text-lg font-bold text-white mb-3">Local-First</h4>
                    <p className="text-white/40 text-xs leading-relaxed uppercase tracking-widest">Zero latency. Zero leak.</p>
                </div>

                <div className="p-8 rounded-[32px] bg-[#0a0a0a] border border-white/5 hover:border-emerald-500/20 transition-all group">
                    <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center mb-6 border border-emerald-500/20">
                        <Lock size={24} className="text-emerald-500" />
                    </div>
                    <h4 className="text-lg font-bold text-white mb-3">E2E Cryptography</h4>
                    <p className="text-white/40 text-xs leading-relaxed uppercase tracking-widest">AES-256 Memory Tunnels.</p>
                </div>

                <div className="p-8 rounded-[32px] bg-[#0a0a0a] border border-white/5 hover:border-purple-500/20 transition-all group">
                    <div className="w-12 h-12 rounded-2xl bg-purple-500/10 flex items-center justify-center mb-6 border border-purple-500/20">
                        <Eye size={24} className="text-purple-500" />
                    </div>
                    <h4 className="text-lg font-bold text-white mb-3">Vision Guard</h4>
                    <p className="text-white/40 text-xs leading-relaxed uppercase tracking-widest">PII Stripping Engines.</p>
                </div>

                <div className="p-8 rounded-[32px] bg-[#0a0a0a] border border-white/5 hover:border-orange-500/20 transition-all group">
                    <div className="w-12 h-12 rounded-2xl bg-orange-500/10 flex items-center justify-center mb-6 border border-orange-500/20">
                        <Zap size={24} className="text-orange-500" />
                    </div>
                    <h4 className="text-lg font-bold text-white mb-3">Deterministic</h4>
                    <p className="text-white/40 text-xs leading-relaxed uppercase tracking-widest">100% Logic Reproducibility.</p>
                </div>
            </div>
        </section>
    );
}
