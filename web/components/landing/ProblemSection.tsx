import { Wind, Activity, Zap, Shield } from "lucide-react";

export function ProblemSection() {
    return (
        <section className="section-spacing w-full max-w-6xl px-6">
            <div className="text-center mb-24">
                <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                    Where Gen-AI <span className="text-red-500">Hits the Wall</span>.
                </h2>
                <p className="text-white/40 text-lg md:text-xl font-light">The expansion debt of generative noise.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-stretch">
                {/* Large Primary Card (Gen Paradox) */}
                <div className="md:col-span-8 p-10 rounded-[32px] border border-white/10 bg-white/[0.02] hover:bg-white/[0.04] transition-all group/reveal overflow-hidden relative">
                    <div className="absolute top-0 right-0 p-8 opacity-5 group-hover/reveal:opacity-10 transition-opacity">
                        <Wind size={200} />
                    </div>
                    <div className="relative z-10 h-full flex flex-col justify-between">
                        <div>
                            <div className="flex justify-between items-start mb-4">
                                <h3 className="text-3xl font-bold text-white">The Digital Amnesia</h3>
                                <div className="opacity-0 group-hover/reveal:opacity-100 group-active/reveal:opacity-100 transition-all duration-500 translate-y-2 group-hover/reveal:translate-y-0 group-active/reveal:translate-y-0 text-[10px] font-mono text-white/40 uppercase tracking-[0.2em] bg-white/5 px-3 py-1 rounded-full border border-white/10">
                                    Recovery: Auto-Persisted | Substrate: SQLite
                                </div>
                            </div>
                            <p className="text-white/50 text-lg leading-relaxed max-w-xl">
                                Generative models are stateless. Sidelith provides the <b>persistent substrate</b>. Eliminate repetitive loops by anchoring every prompt to a permanent semantic truth.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Smaller Card (Truth Decay) */}
                <div className="md:col-span-4 p-8 rounded-[32px] border border-red-500/10 bg-red-500/[0.02] hover:bg-red-500/[0.04] transition-all group/reveal">
                    <div className="flex justify-between items-start mb-6">
                        <Activity className="text-red-500" size={32} />
                        <div className="opacity-0 group-hover/reveal:opacity-100 transition-all duration-500 scale-95 group-hover/reveal:scale-100 text-[8px] font-mono text-red-500/60 uppercase tracking-widest text-right leading-tight">
                            Validation: Merkle-Hash<br />
                            Integrity: SHA-256
                        </div>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-4">The Truth Decay</h3>
                    <p className="text-white/40 leading-relaxed text-sm">
                        Documentation is a claim; Code is the evidence. Sidelith bridges the gap with Merkle-validated state.
                    </p>
                </div>

                {/* Smaller Card (Context Saturation) */}
                <div className="md:col-span-4 p-8 rounded-[32px] border border-orange-500/10 bg-orange-500/[0.02] hover:bg-orange-500/[0.04] transition-all group/reveal">
                    <div className="flex justify-between items-start mb-6">
                        <Zap className="text-orange-500" size={32} />
                        <div className="opacity-0 group-hover/reveal:opacity-100 transition-all duration-500 scale-95 group-hover/reveal:scale-100 text-[8px] font-mono text-orange-500/60 uppercase tracking-widest text-right leading-tight">
                            Signal: High-Fidelity<br />
                            Noise Isolation: Binary
                        </div>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-4">Context Rot</h3>
                    <p className="text-white/40 leading-relaxed text-sm">
                        Reasoning degrades as noise accumulates. Sidelith acts as the antibody to generative entropy.
                    </p>
                </div>

                {/* Medium Card (Governance) */}
                <div className="md:col-span-8 p-8 rounded-[32px] border border-yellow-500/10 bg-yellow-500/[0.02] hover:bg-yellow-500/[0.04] transition-all group/reveal relative overflow-hidden">
                    <div className="absolute -bottom-6 -right-6 opacity-5 group-hover/reveal:opacity-10 transition-opacity">
                        <Shield size={160} />
                    </div>
                    <div className="relative z-10 flex justify-between items-start">
                        <div className="max-w-lg">
                            <h3 className="text-2xl font-bold text-white mb-4">The Governance Moat</h3>
                            <p className="text-white/50 leading-relaxed">
                                Every architectural decision is cryptographically sealed. Prevent reasoning drift with 100% auditability.
                            </p>
                        </div>
                        <div className="opacity-0 group-hover/reveal:opacity-100 transition-all duration-500 translate-x-4 group-hover/reveal:translate-x-0 text-[10px] font-mono text-yellow-500/60 uppercase tracking-[0.2em] bg-yellow-500/5 px-4 py-2 rounded-xl border border-yellow-500/10 text-right leading-relaxed">
                            Policy: Local-Only<br />
                            Encryption: AES-256
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
