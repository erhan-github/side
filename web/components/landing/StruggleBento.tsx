export function StruggleBento() {
    return (
        <section className="section-spacing w-full max-w-6xl px-6">
            <div className="text-center mb-24">
                <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                    The Cost of <span className="text-orange-500">Struggle</span>.
                </h2>
                <p className="text-white/40 text-lg md:text-xl font-light max-w-2xl mx-auto">
                    Every manual correction is a leak in your cognitive treasury.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Friction Point A */}
                <div className="p-8 rounded-[32px] border border-white/5 bg-white/[0.01] hover:border-white/10 transition-all flex flex-col justify-between group">
                    <div>
                        <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center mb-6 group-hover:bg-white/10 transition-colors">
                            <span className="text-xl font-bold text-white/20">01</span>
                        </div>
                        <h4 className="text-xl font-bold text-white mb-4">Semantic Drift</h4>
                        <p className="text-white/40 text-sm leading-relaxed mb-8">
                            When your agent solves the same bug for the 3rd time because it "forgot" the previous fix. Persistence is the only cure.
                        </p>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="h-1 flex-1 bg-white/5 rounded-full overflow-hidden">
                            <div className="h-full bg-orange-500/40 w-3/4"></div>
                        </div>
                        <span className="text-[10px] font-mono text-orange-500/60 uppercase tracking-widest">CRITICAL LEAK</span>
                    </div>
                </div>

                {/* Friction Point B */}
                <div className="p-8 rounded-[32px] border border-white/5 bg-white/[0.01] hover:border-white/10 transition-all flex flex-col justify-between group">
                    <div>
                        <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center mb-6 group-hover:bg-white/10 transition-colors">
                            <span className="text-xl font-bold text-white/20">02</span>
                        </div>
                        <h4 className="text-xl font-bold text-white mb-4">Context Suffocation</h4>
                        <p className="text-white/40 text-sm leading-relaxed mb-8">
                            Loading 50 files into context because the agent doesn't know where to look. Sidelith provides the precision laser.
                        </p>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="h-1 flex-1 bg-white/5 rounded-full overflow-hidden">
                            <div className="h-full bg-red-500/40 w-[92%]"></div>
                        </div>
                        <span className="text-[10px] font-mono text-red-500/60 uppercase tracking-widest">HIGH WASTE</span>
                    </div>
                </div>

                {/* Friction Point C */}
                <div className="p-8 rounded-[32px] border border-white/5 bg-white/[0.01] hover:border-white/10 transition-all flex flex-col justify-between group">
                    <div>
                        <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center mb-6 group-hover:bg-white/10 transition-colors">
                            <span className="text-xl font-bold text-white/20">03</span>
                        </div>
                        <h4 className="text-xl font-bold text-white mb-4">Regressive Reasoning</h4>
                        <p className="text-white/40 text-sm leading-relaxed mb-8">
                            A fix in module A breaks module B because the "local-only" context blinded the model. Global ontology is mandatory.
                        </p>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="h-1 flex-1 bg-white/5 rounded-full overflow-hidden">
                            <div className="h-full bg-blue-500/40 w-[61%]"></div>
                        </div>
                        <span className="text-[10px] font-mono text-blue-500/60 uppercase tracking-widest">UNKNOWN RISK</span>
                    </div>
                </div>
            </div>
        </section>
    );
}
