import { User, Bot, Zap, Shield, Database, ArrowRight, Brain, FileCode, CheckCircle2, XCircle, Filter, Sparkles } from "lucide-react";

export function MiddlewareFlow() {
    return (
        <section className="section-spacing w-full max-w-7xl px-4 py-24 relative z-10">
            <div className="text-center mb-20">
                <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
                    The <span className="text-blue-400">Context Middleware</span>.
                </h2>
                <p className="text-white/40 text-lg font-light max-w-2xl mx-auto">
                    We intercept the conversation to inject memory, enforce rules, and fix amnesia.
                </p>
            </div>

            {/* THE VISUAL STAGE */}
            <div className="relative w-full max-w-5xl mx-auto bg-[#0a0a0a] rounded-[40px] border border-white/5 p-8 md:p-12 overflow-hidden shadow-2xl group selection:bg-blue-500/20">

                {/* Background Grid & GLow */}
                <div className="absolute inset-0 bg-grid-white/[0.02] bg-[length:32px_32px]" />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-blue-500/5 blur-[100px] rounded-full" />

                <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8 md:gap-0">

                    {/* --- NODE 1: USER (THE CREATOR) --- */}
                    <div className="flex flex-col items-center z-20 w-48 shrink-0">
                        <div className="w-20 h-20 rounded-2xl bg-white flex items-center justify-center shadow-[0_0_50px_rgba(255,255,255,0.2)] border-2 border-white mb-6 relative">
                            <User size={32} className="text-black" />
                            <div className="absolute -bottom-3 px-3 py-1 bg-white text-black text-[10px] font-bold uppercase tracking-widest rounded-full border border-black">
                                CREATOR
                            </div>
                        </div>
                        <div className="text-center">
                            <h4 className="text-white font-bold mb-2">High Intent</h4>
                            <div className="flex flex-col gap-1 text-[10px] text-white/40 font-mono uppercase tracking-wide">
                                <span>"Refactor Auth"</span>
                                <span>"Fix Race Condition"</span>
                            </div>
                        </div>
                    </div>

                    {/* --- THE MIDDLEWARE BRIDGE (SIDELITH) --- */}
                    <div className="flex-1 w-full mx-4 md:mx-8 relative h-[300px] md:h-[180px] flex items-center justify-center">

                        {/* PATH 1: THE BROKEN PATH (Old Way) - Top Arch */}
                        <div className="absolute top-0 left-0 right-0 h-full pointer-events-none opacity-20">
                            <svg className="w-full h-full overflow-visible">
                                <path d="M 0,90 Q 50,-50 100,90" fill="none" stroke="#ef4444" strokeWidth="2" strokeDasharray="6 6" vectorEffect="non-scaling-stroke" className="md:hidden" />
                                <path d="M 10,90 C 150,-50 450,-50 600,90" fill="none" stroke="#ef4444" strokeWidth="2" strokeDasharray="8 8" vectorEffect="non-scaling-stroke" className="hidden md:block" />
                            </svg>
                            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-2 flex items-center gap-2 bg-red-500/10 border border-red-500/20 px-3 py-1 rounded-full text-red-400 text-[10px] font-bold uppercase tracking-widest">
                                <XCircle size={12} /> Context Amnesia
                            </div>
                        </div>


                        {/* PATH 2: THE SIDELITH TUNNEL (Main linear flow) */}
                        <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden relative">
                            {/* The Beam */}
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-500 to-transparent w-1/2 animate-[shimmer_2s_infinite_linear]" />
                        </div>

                        {/* THE MIDDLEWARE PROCESSOR (Center Node) */}
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center z-30">
                            <div className="relative w-32 h-32 rounded-full border border-blue-500/30 bg-[#0a0a0a] flex items-center justify-center shadow-[0_0_60px_rgba(59,130,246,0.15)] group-hover:border-blue-400/60 transition-colors duration-500">
                                {/* Orbiting Particles */}
                                <div className="absolute inset-0 rounded-full border border-transparent border-t-blue-500/50 animate-[spin_3s_linear_infinite]" />
                                <div className="absolute inset-2 rounded-full border border-transparent border-b-purple-500/50 animate-[spin_5s_linear_infinite_reverse]" />

                                {/* Core Icons Paginating */}
                                <div className="relative z-10 flex flex-col items-center gap-1">
                                    <div className="flex gap-2 mb-1">
                                        <Database size={16} className="text-blue-400" />
                                        <Shield size={16} className="text-emerald-400" />
                                    </div>
                                    <span className="text-white font-bold tracking-widest text-xs">SIDELITH</span>
                                    <span className="text-[8px] text-blue-400 uppercase tracking-widest">Active State</span>
                                </div>
                            </div>

                            {/* Processing Labels */}
                            {/* Processing Labels */}
                            <div className="absolute top-[130px] w-[340px] grid grid-cols-2 gap-2">
                                <div className="px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-bold uppercase tracking-widest flex items-center justify-center gap-1.5 animate-in fade-in zoom-in duration-500 delay-100">
                                    <Brain size={12} /> Inject Memory
                                </div>
                                <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-widest flex items-center justify-center gap-1.5 animate-in fade-in zoom-in duration-500 delay-200">
                                    <Shield size={12} /> Guard Rails
                                </div>
                                <div className="px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-500 text-[10px] font-bold uppercase tracking-widest flex items-center justify-center gap-1.5 animate-in fade-in zoom-in duration-500 delay-300">
                                    <Filter size={12} /> Prune Noise
                                </div>
                                <div className="px-3 py-1.5 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-400 text-[10px] font-bold uppercase tracking-widest flex items-center justify-center gap-1.5 animate-in fade-in zoom-in duration-500 delay-400">
                                    <Sparkles size={12} /> Match Patterns
                                </div>
                            </div>
                        </div>

                    </div>

                    {/* --- NODE 3: LLM (THE BRAIN) --- */}
                    <div className="flex flex-col items-center z-20 w-48 shrink-0">
                        <div className="w-20 h-20 rounded-2xl bg-[#0a0a0a] border border-purple-500/50 flex items-center justify-center shadow-[0_0_50px_rgba(168,85,247,0.2)] mb-6 relative">
                            <Bot size={32} className="text-purple-400" />
                            <div className="absolute -bottom-3 px-3 py-1 bg-purple-500/10 text-purple-400 text-[10px] font-bold uppercase tracking-widest rounded-full border border-purple-500/30">
                                MODEL
                            </div>
                        </div>
                        <div className="text-center">
                            <h4 className="text-white font-bold mb-2">Perfect Response</h4>
                            <div className="flex flex-col gap-1 text-[10px] text-white/40 font-mono uppercase tracking-wide">
                                <span className="text-emerald-400 flex items-center justify-center gap-1"><CheckCircle2 size={10} /> Context Aware</span>
                                <span className="text-emerald-400 flex items-center justify-center gap-1"><CheckCircle2 size={10} /> Policy Compliant</span>
                            </div>
                        </div>
                    </div>

                </div>

                {/* Mobile Flow Connectors */}
                <div className="md:hidden flex flex-col items-center gap-2 my-8 opacity-20">
                    <ArrowRight className="rotate-90" />
                    <ArrowRight className="rotate-90" />
                    <ArrowRight className="rotate-90" />
                </div>

            </div>

            {/* Context Comparison Caption */}
            <div className="mt-12 text-center max-w-4xl mx-auto">
                <p className="text-lg text-white/50 font-light leading-relaxed">
                    <span className="opacity-60 decoration-white/20 line-through decoration-1">You are used to "Stateless Chat" (The LLM knows nothing).</span>
                    <br className="my-2 block" />
                    <span className="hidden md:inline mx-3 text-white/10">↓</span>
                    <span className="text-white font-medium block mt-2">
                        Sidelith enforces <span className="text-blue-400">"Stateful Context"</span>.
                        <span className="block text-white/60 text-base mt-1 font-light">
                            (It retains the <span className="text-white/90">strategic intent</span> behind your architecture).
                        </span>
                    </span>
                </p>
            </div>
        </section>
    );
}
