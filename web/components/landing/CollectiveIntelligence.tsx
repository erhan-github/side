import { Activity } from "lucide-react";

export function CollectiveIntelligence() {
    return (
        <section className="section-spacing w-full max-w-4xl px-6 py-20 bg-gradient-to-b from-white/[0.02] to-transparent rounded-[40px] border border-white/5 relative z-10 mb-32">
            <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center mb-8 border border-emerald-500/20">
                    <Activity size={32} className="text-emerald-500" />
                </div>
                <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">Community <span className="text-emerald-500">Immunity</span>.</h2>
                <p className="text-white/40 text-lg font-light leading-relaxed max-w-2xl">
                    When one developer solves a logic puzzle, Sidelith's <span className="text-white">Shared Knowledge Base</span> shares the structural solution with the network. You benefit from the community's immunization without ever sharing a line of code.
                </p>

                <div className="mt-12 flex gap-8">
                    <div className="text-center">
                        <div className="text-3xl font-bold text-white">Verified</div>
                        <div className="text-[10px] text-white/30 uppercase tracking-[0.2em] mt-2">Solutions</div>
                    </div>
                    <div className="w-px h-12 bg-white/10"></div>
                    <div className="text-center">
                        <div className="text-3xl font-bold text-white">None</div>
                        <div className="text-[10px] text-white/30 uppercase tracking-[0.2em] mt-2">Data Leaks</div>
                    </div>
                </div>
            </div>
        </section>
    );
}
