import { AlertTriangle, Clock, ZapOff } from "lucide-react";

export function StruggleBento() {
    return (
        <section className="section-spacing w-full max-w-6xl px-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[250px]">

                {/* Card 1: AI Forgets Your Fixes */}
                <div className="group md:col-span-1 rounded-[32px] bg-[#0A0A0A] border border-white/5 p-8 relative overflow-hidden hover:border-white/10 transition-colors">
                    <div className="mb-6 w-12 h-12 rounded-2xl bg-red-500/10 flex items-center justify-center">
                        <ZapOff className="text-red-400" size={24} />
                    </div>
                    <h4 className="text-xl font-bold text-white mb-2">AI Forgets Your Fixes</h4>
                    <p className="text-white/50 text-sm leading-relaxed">
                        When AI solves the same bug for the 3rd time because it forgot the previous fix.
                    </p>
                </div>

                {/* Card 2: Wastes Tokens (Large) */}
                <div className="group md:col-span-2 rounded-[32px] bg-[#0A0A0A] border border-white/5 p-8 relative overflow-hidden hover:border-white/10 transition-colors">
                    <div className="mb-6 w-12 h-12 rounded-2xl bg-orange-500/10 flex items-center justify-center">
                        <AlertTriangle className="text-orange-400" size={24} />
                    </div>
                    <h4 className="text-xl font-bold text-white mb-2">Wastes Tokens</h4>
                    <p className="text-white/50 text-sm leading-relaxed max-w-md">
                        Loading 50 files into context because AI doesn't know where to look.
                        Stateful context solves this by only injecting what matters.
                    </p>
                </div>

                {/* Card 3: Breaks Related Code */}
                <div className="group md:col-span-3 rounded-[32px] bg-[#0A0A0A] border border-white/5 p-8 relative overflow-hidden hover:border-white/10 transition-colors flex flex-col md:flex-row items-center gap-8">
                    <div className="flex-1">
                        <div className="mb-6 w-12 h-12 rounded-2xl bg-purple-500/10 flex items-center justify-center">
                            <Clock className="text-purple-400" size={24} />
                        </div>
                        <h4 className="text-xl font-bold text-white mb-2">Breaks Related Code</h4>
                        <p className="text-white/50 text-sm leading-relaxed">
                            A fix in module A breaks module B because AI only saw part of your codebase.
                        </p>
                    </div>

                    {/* Visual: Broken Link */}
                    <div className="flex-1 w-full max-w-sm p-4 rounded-xl bg-black/40 border border-white/5 font-mono text-xs text-white/40">
                        <div className="text-green-400 mb-2">+ function updateUser() {'{'}</div>
                        <div className="text-red-400 mb-2">-    // api.update() broken ref</div>
                        <div className="bg-red-500/10 text-red-300 p-2 rounded border border-red-500/20">
                            Error: 'api' is undefined in 'Profile.tsx'
                        </div>
                    </div>
                </div>

            </div>
        </section>
    );
}
