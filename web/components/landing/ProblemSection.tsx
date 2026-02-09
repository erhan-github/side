import { Wind, Activity, Zap, Shield } from "lucide-react";

export function ProblemSection() {
    return (
        <section className="py-16 w-full max-w-6xl px-6">
            <div className="text-center mb-16">
                <h2 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-100 to-gray-400 mb-6">
                    AI tools forget between conversations
                </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">
                {/* Pain Card 1 */}
                <div className="p-8 rounded-[32px] border border-white/10 bg-white/[0.02] hover:bg-white/[0.04] transition-all group relative overflow-hidden flex flex-col">
                    <div className="mb-6 flex justify-between items-start">
                        <div className="p-3 rounded-2xl bg-white/5 border border-white/10">
                            <Activity className="text-red-400" size={24} />
                        </div>
                        <span className="text-xs font-mono text-red-400 border border-red-500/20 bg-red-500/10 px-3 py-1 rounded-full uppercase tracking-wider">
                            2 hours wasted
                        </span>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-3">Same Bug, Third Time</h3>
                    <p className="text-white/50 leading-relaxed text-sm">
                        You fixed this race condition yesterday. Today, Cursor suggests the same broken code because it has no memory of your fix.
                    </p>
                </div>

                {/* Pain Card 2 */}
                <div className="p-8 rounded-[32px] border border-white/10 bg-white/[0.02] hover:bg-white/[0.04] transition-all group relative overflow-hidden flex flex-col">
                    <div className="mb-6 flex justify-between items-start">
                        <div className="p-3 rounded-2xl bg-white/5 border border-white/10">
                            <Wind className="text-orange-400" size={24} />
                        </div>
                        <span className="text-xs font-mono text-orange-400 border border-orange-500/20 bg-orange-500/10 px-3 py-1 rounded-full uppercase tracking-wider">
                            30 min/day wasted
                        </span>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-3">Re-explaining Architecture</h3>
                    <p className="text-white/50 leading-relaxed text-sm">
                        "We use Redux for state." "Our API is GraphQL." "Components go in /src/ui." You type this every single conversation.
                    </p>
                </div>

                {/* Pain Card 3 */}
                <div className="p-8 rounded-[32px] border border-white/10 bg-white/[0.02] hover:bg-white/[0.04] transition-all group relative overflow-hidden flex flex-col">
                    <div className="mb-6 flex justify-between items-start">
                        <div className="p-3 rounded-2xl bg-white/5 border border-white/10">
                            <Zap className="text-yellow-400" size={24} />
                        </div>
                        <span className="text-xs font-mono text-yellow-400 border border-yellow-500/20 bg-yellow-500/10 px-3 py-1 rounded-full uppercase tracking-wider">
                            1 hr/day fixing
                        </span>
                    </div>
                    <h3 className="text-xl font-bold text-white mb-3">Breaking Patterns</h3>
                    <p className="text-white/50 leading-relaxed text-sm">
                        AI suggests Axios when you use Fetch. Suggests class components when you use hooks. It doesn't know your style.
                    </p>
                </div>
            </div>
        </section>
    );
}
