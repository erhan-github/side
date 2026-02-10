import { Shield, Lock, Eye, Zap } from "lucide-react";

export function DefensiveMoats() {
    return (
        <section className="w-full max-w-6xl px-6 py-16 relative overflow-hidden">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-blue-500/5 blur-[120px] rounded-full -z-10" />

            <div className="text-center mb-16">
                <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                    Built for <span className="text-blue-400">Privacy</span>.
                </h2>
                <p className="text-white/40 text-lg md:text-xl font-light">Your code never leaves your machine. Local-first by design.</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
                <div className="p-4 md:p-8 rounded-[24px] md:rounded-[32px] bg-[#0a0a0a] border border-white/5 hover:border-blue-500/20 transition-all group">
                    <div className="w-10 h-10 md:w-12 md:h-12 rounded-xl md:rounded-2xl bg-blue-500/10 flex items-center justify-center mb-4 md:mb-6 border border-blue-500/20">
                        <Shield size={24} className="text-blue-500" />
                    </div>
                    <h4 className="text-lg font-bold text-white mb-3">Local-First</h4>
                    <p className="text-white/40 text-xs leading-relaxed uppercase tracking-widest">Zero latency. Zero leak.</p>
                </div>

                <div className="p-4 md:p-8 rounded-[24px] md:rounded-[32px] bg-[#0a0a0a] border border-white/5 hover:border-emerald-500/20 transition-all group">
                    <div className="w-10 h-10 md:w-12 md:h-12 rounded-xl md:rounded-2xl bg-emerald-500/10 flex items-center justify-center mb-4 md:mb-6 border border-emerald-500/20">
                        <Lock size={24} className="text-emerald-500" />
                    </div>
                    <h4 className="text-lg font-bold text-white mb-3">E2E Cryptography</h4>
                    <p className="text-white/40 text-xs leading-relaxed uppercase tracking-widest">Encrypted local storage.</p>
                </div>

                <div className="p-4 md:p-8 rounded-[24px] md:rounded-[32px] bg-[#0a0a0a] border border-white/5 hover:border-purple-500/20 transition-all group">
                    <div className="w-10 h-10 md:w-12 md:h-12 rounded-xl md:rounded-2xl bg-purple-500/10 flex items-center justify-center mb-4 md:mb-6 border border-purple-500/20">
                        <Eye size={24} className="text-purple-500" />
                    </div>
                    <h4 className="text-lg font-bold text-white mb-3">Privacy Screen</h4>
                    <p className="text-white/40 text-xs leading-relaxed uppercase tracking-widest">Personal Data Removal (PII).</p>
                </div>

                <div className="p-4 md:p-8 rounded-[24px] md:rounded-[32px] bg-[#0a0a0a] border border-white/5 hover:border-orange-500/20 transition-all group">
                    <div className="w-10 h-10 md:w-12 md:h-12 rounded-xl md:rounded-2xl bg-orange-500/10 flex items-center justify-center mb-4 md:mb-6 border border-orange-500/20">
                        <Zap size={24} className="text-orange-500" />
                    </div>
                    <h4 className="text-lg font-bold text-white mb-3">Predictable</h4>
                    <p className="text-white/40 text-xs leading-relaxed uppercase tracking-widest">Consistent Logic.</p>
                </div>
            </div>
        </section>
    );
}
