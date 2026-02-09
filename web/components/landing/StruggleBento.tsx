import { AlertTriangle, Clock, ZapOff } from "lucide-react";

export function StruggleBento() {
    return (
        <section className="py-16 w-full max-w-6xl mx-auto px-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[250px]">

                {/* Card 1: AI Forgets Your Fixes */}
                <div className="group md:col-span-1 rounded-[32px] bg-[#0A0A0A] border border-white/10 p-8 relative overflow-hidden hover:border-white/20 transition-colors">
                    <div className="mb-6 w-12 h-12 rounded-2xl bg-red-500/10 flex items-center justify-center border border-red-500/20">
                        <ZapOff className="text-red-400" size={24} />
                    </div>
                    <h4 className="text-xl font-bold text-white mb-3">AI Forgets Your Fixes</h4>
                    <p className="text-zinc-400 text-sm leading-relaxed">
                        When AI solves the same bug for the 3rd time because it forgot the previous fix.
                    </p>
                </div>

                {/* Card 2: Wastes Tokens (Large) */}
                <div className="group md:col-span-2 rounded-[32px] bg-[#0A0A0A] border border-white/10 p-8 relative overflow-hidden hover:border-white/20 transition-colors">
                    <div className="mb-6 w-12 h-12 rounded-2xl bg-orange-500/10 flex items-center justify-center border border-orange-500/20">
                        <AlertTriangle className="text-orange-400" size={24} />
                    </div>
                    <h4 className="text-xl font-bold text-white mb-3">Wastes Tokens</h4>
                    <p className="text-zinc-400 text-sm leading-relaxed max-w-md">
                        Loading 50 files into context because AI doesn't know where to look.
                        Stateful context solves this by only injecting what matters.
                    </p>
                </div>

                {/* Card 3: Breaks Related Code */}
                <div className="group md:col-span-3 rounded-[32px] bg-[#0A0A0A] border border-white/10 p-8 relative overflow-hidden hover:border-white/20 transition-colors flex flex-col md:flex-row items-center gap-12">
                    <div className="flex-1">
                        <div className="mb-6 w-12 h-12 rounded-2xl bg-purple-500/10 flex items-center justify-center border border-purple-500/20">
                            <Clock className="text-purple-400" size={24} />
                        </div>
                        <h4 className="text-xl font-bold text-white mb-3">Breaks Related Code</h4>
                        <p className="text-zinc-400 text-sm leading-relaxed max-w-lg">
                            A fix in module A breaks module B because AI only saw part of your codebase.
                            Sidelith provides the global graph to prevent this.
                        </p>
                    </div>

                    {/* Visual: Broken Link */}
                    <div className="flex-1 w-full max-w-md p-6 rounded-2xl bg-black/40 border border-white/10 font-mono text-xs text-zinc-500 shadow-xl backdrop-blur-sm">
                        <div className="flex items-center gap-2 mb-4 border-b border-white/5 pb-2">
                            <span className="text-zinc-600">Profile.tsx</span>
                        </div>
                        <div className="text-emerald-400/80 mb-2">+ function updateUser() {'{'}</div>
                        <div className="text-red-400/80 mb-4">-    // api.update() broken ref</div>
                        <div className="bg-red-500/10 text-red-300 p-3 rounded-lg border border-red-500/20 flex items-start gap-2">
                            <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                            <span>Error: 'api' is undefined in 'Profile.tsx'</span>
                        </div>
                    </div>
                </div>

            </div>
        </section>
    );
}
