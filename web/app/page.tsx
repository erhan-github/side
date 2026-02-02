import { ArrowRight, Terminal, Shield, Zap, Cpu, Database, Command, Check, Activity, Lock, Globe, Sparkles } from "lucide-react";
import { InstallWidget } from "../components/InstallWidget";

export default function Home() {
    return (
        <main className="min-h-screen flex flex-col items-center overflow-hidden bg-void text-foreground selection:bg-neon/20">
            {/* 1. HERO SECTION */}
            <section className="w-full max-w-6xl px-6 flex flex-col items-center text-center z-10 pt-32 pb-12">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-mono text-xs text-subtle mb-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                    <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                    <span>They fight for Models. <span className="text-white font-bold ml-1">We win on Memory.</span></span>
                </div>

                <h1 className="text-hero mb-6 bg-gradient-to-b from-white to-white/60 bg-clip-text text-transparent animate-in fade-in slide-in-from-bottom-8 duration-1000 fill-mode-both">
                    Fix Context Entropy.
                </h1>

                <p className="text-body-lg text-white/60 max-w-2xl mb-12 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-200 fill-mode-both">
                    The <span className="text-white">Deterministic Control Plane</span> for your LLMs. <br />
                    Stop guessing. Start enforcing.
                </p>


            </section>

            {/* 2. THE PROBLEM (Where AI Fails) */}
            <section className="section-spacing w-full max-w-6xl px-6 text-center animate-in fade-in slide-in-from-bottom-16 duration-1000 delay-300">
                <div className="mb-16">
                    <h2 className="text-h2 mb-4 text-white">
                        Where Coding with AI <span className="text-red-500">Fails</span>.
                    </h2>
                    <div className="inline-block px-4 py-1.5 rounded-full border border-red-500/20 bg-red-500/5 text-red-400 font-mono text-xs tracking-widest uppercase">
                        The Broken Cycle
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                    {/* Card 1: Entropy (Stability) */}
                    <div className="p-8 rounded-3xl border border-red-500/10 bg-red-500/[0.02] hover:bg-red-500/[0.04] transition-colors group">
                        <div className="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center text-red-400 mb-6 group-hover:text-red-300 transition-colors">
                            <Activity size={24} />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-2">The Entropy Theorem</h3>
                        <p className="text-xs font-mono text-red-400 uppercase tracking-wider mb-4">Stability Risk</p>
                        <p className="text-white/70 leading-relaxed mb-4">
                            <b>"It worked yesterday."</b> <br />
                            LLMs are probabilistic. Code is deterministic. Without a sovereign state machine, every prompt increases the entropy of your codebase.
                        </p>
                    </div>

                    {/* Card 2: Context (Memory) */}
                    <div className="p-8 rounded-3xl border border-orange-500/10 bg-orange-500/[0.02] hover:bg-orange-500/[0.04] transition-colors group">
                        <div className="w-12 h-12 rounded-xl bg-orange-500/10 flex items-center justify-center text-orange-400 mb-6 group-hover:text-orange-300 transition-colors">
                            <Zap size={24} />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-2">Context Saturation</h3>
                        <p className="text-xs font-mono text-orange-400 uppercase tracking-wider mb-4">Scalability Bottleneck</p>
                        <p className="text-white/70 leading-relaxed mb-4">
                            <b>"Goldfish Memory."</b> <br />
                            RAG is lossy. As you scale to 10k+ files, AI becomes "senile", forcing you to re-explain your own architecture daily.
                        </p>
                    </div>

                    {/* Card 3: Governance (Security) */}
                    <div className="p-8 rounded-3xl border border-yellow-500/10 bg-yellow-500/[0.02] hover:bg-yellow-500/[0.04] transition-colors group">
                        <div className="w-12 h-12 rounded-xl bg-yellow-500/10 flex items-center justify-center text-yellow-400 mb-6 group-hover:text-yellow-300 transition-colors">
                            <Shield size={24} />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-2">The Governance Moat</h3>
                        <p className="text-xs font-mono text-yellow-400 uppercase tracking-wider mb-4">Enterprise IP Risk</p>
                        <p className="text-white/70 leading-relaxed mb-4">
                            <b>"Your secrets are leaking."</b> <br />
                            Cloud LLMs are data vacuums. Sending proprietary logic to an external API violates the core tenant of Sovereign Intelligence.
                        </p>
                    </div>
                </div>
            </section>

            {/* 3. THE SOLUTION (The Sovereign Control Loop) */}
            {/* I will use `multi_replace_file_content` to hit Hero/Problem (Top) and Pricing (Bottom). */}



            {/* 3. THE SOLUTION (How We Fix It) */}
            <section className="section-spacing w-full max-w-6xl px-4 z-10 relative">
                <div className="text-center mb-16">
                    <div className="inline-block px-4 py-1.5 rounded-full border border-neon/20 bg-neon/5 text-neon font-mono text-xs tracking-widest uppercase mb-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                        The Antidote to Entropy
                    </div>
                    <h2 className="text-hero mb-6 text-white animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300">
                        How We <span className="text-neon">Fix It</span>.
                    </h2>
                    <p className="text-xl md:text-2xl text-white/60 max-w-3xl mx-auto leading-relaxed animate-in fade-in slide-in-from-bottom-8 duration-700 delay-500">
                        What if you could mathematically guarantee context? <br />
                        The <b>Reinforcement Loop</b> resolves the broken AI coding cycle.
                    </p>
                </div>

                {/* THE SOVEREIGN SOLAR SYSTEM (HEXAGON ORBIT) */}
                <div className="w-full max-w-6xl mx-auto mb-20 relative animate-in fade-in zoom-in-95 duration-1000 delay-500 min-h-[900px] hidden md:block">

                    {/* Background Galaxy & Title */}
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-[700px] h-[700px] rounded-full border border-white/5 bg-white/[0.01] animate-[spin_100s_linear_infinite]" />
                        <div className="absolute text-[250px] font-heading font-bold text-white/[0.02] pointer-events-none select-none">
                            O
                        </div>
                    </div>

                    {/* Connecting Path (Hexagon Orbit & Flows) */}
                    <svg className="absolute inset-0 w-full h-full pointer-events-none z-0" viewBox="0 0 1000 800" fill="none">
                        <defs>
                            <linearGradient id="cycle-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stopColor="#00ff9d" />
                                <stop offset="50%" stopColor="#f59e0b" />
                                <stop offset="100%" stopColor="#3b82f6" />
                            </linearGradient>
                            <marker id="arrow-head" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                                <polygon points="0 0, 10 3.5, 0 7" fill="white" />
                            </marker>
                            <marker id="arrow-head-gold" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                                <polygon points="0 0, 10 3.5, 0 7" fill="#f59e0b" />
                            </marker>
                        </defs>

                        {/* Orbit Path (Subtle) */}
                        <circle cx="500" cy="400" r="350" stroke="url(#cycle-gradient)" strokeWidth="1" strokeDasharray="10 10" className="opacity-20" />

                        {/* 1. INTENT LINE (You -> Intent) */}
                        <path id="intent-line" d="M 500 350 L 680 200" stroke="white" strokeWidth="2" strokeDasharray="4 4" className="animate-[dash_1s_linear_infinite]" markerEnd="url(#arrow-head)" />

                        {/* 2. DIODE BRIDGE (Memory -> Compute) */}
                        <path id="diode-line" d="M 450 450 L 230 413" stroke="white" strokeOpacity="0.6" strokeWidth="2" strokeDasharray="4 4" markerEnd="url(#arrow-head)" className="animate-[dash_3s_linear_infinite]" />

                        {/* Invisible Path for Text Correction (Left-to-Right) */}
                        <path id="diode-text-path" d="M 230 413 L 450 450" fill="none" stroke="none" />

                        <text dy="-10">
                            <textPath href="#diode-text-path" startOffset="50%" textAnchor="middle" className="fill-white/70 text-[10px] uppercase font-mono tracking-widest font-bold">
                                [ANON_PATTERNS]
                            </textPath>
                        </text>

                        {/* 3. LEARNING LOOP (Editor -> Memory) */}
                        <path id="learning-line" d="M 280 180 Q 380 290 450 370" stroke="#f59e0b" strokeWidth="2" className="animate-pulse opacity-80" strokeLinecap="round" markerEnd="url(#arrow-head-gold)" />
                        <text dy="-10">
                            <textPath href="#learning-line" startOffset="50%" textAnchor="middle" className="fill-amber-500 text-[10px] font-bold font-mono tracking-widest">
                                VERIFY & SAVE
                            </textPath>
                        </text>
                    </svg>

                    {/* --- THE MONARCH CENTER (GRAVITY) --- */}
                    <div className="absolute top-[320px] left-1/2 -translate-x-1/2 flex flex-col items-center text-center z-40 group">
                        {/* YOU */}
                        <div className="w-24 h-24 rounded-full bg-white flex items-center justify-center shadow-[0_0_80px_rgba(255,255,255,0.4)] relative z-20 border-4 border-[#0a0a0a]">
                            <span className="text-black font-bold font-mono text-xl tracking-widest relative z-50">YOU</span>
                        </div>
                        {/* Connector */}
                        <div className="h-8 w-px bg-gradient-to-b from-white to-amber-500"></div>
                        {/* MEMORY */}
                        <div className="w-20 h-20 rounded-2xl bg-[#0a0a0a] border border-amber-500/50 flex items-center justify-center shadow-[0_0_40px_rgba(245,158,11,0.3)] relative z-10 group-hover:border-amber-500 transition-colors">
                            <Database size={28} className="text-amber-500" />
                            <div className="absolute -top-3 -right-3 bg-amber-500 text-black p-1.5 rounded-full"><Lock size={12} /></div>
                        </div>
                        <div className="mt-4 bg-[#0a0a0a]/80 backdrop-blur px-4 py-2 rounded-lg border border-white/10">
                            <h4 className="text-white font-bold text-sm tracking-widest">THE OPERATOR</h4>
                            <p className="text-[10px] text-white/50 uppercase tracking-wider">Long-Term Memory</p>
                        </div>
                    </div>


                    {/* --- THE HEXAGON ORBIT (6 NODES) --- */}

                    {/* Phase 0: INTENT (Top Right - 1:00) */}
                    <div className="absolute top-[100px] right-[20%] flex flex-col items-center text-center z-10 group">
                        <div className="w-16 h-16 rounded-2xl bg-[#0a0a0a] border border-white flex items-center justify-center shadow-[0_0_30px_rgba(255,255,255,0.2)] mb-4">
                            <Sparkles size={24} className="text-white animate-pulse" />
                        </div>
                        <h4 className="text-white font-bold font-mono text-sm tracking-widest mb-1">00. INTENT</h4>
                        <p className="text-xs text-white/50 max-w-[150px]">The Spark.</p>
                    </div>

                    {/* Phase 1: AWARENESS (Right - 3:00) */}
                    <div className="absolute top-1/2 -translate-y-[100px] right-[5%] flex flex-col items-center text-center z-10 group">
                        <div className="w-16 h-16 rounded-2xl bg-[#0a0a0a] border border-white/10 flex items-center justify-center shadow-2xl mb-4 group-hover:border-neon/50 transition-colors">
                            <Database size={24} className="text-white/40 group-hover:text-neon transition-colors" />
                        </div>
                        <h4 className="text-neon font-bold font-mono text-sm tracking-widest mb-1">01. AWARENESS</h4>
                        <p className="text-xs text-white/50 max-w-[150px]">The Map.</p>
                    </div>

                    {/* Phase 2: CONTEXT (Bottom Right - 5:00) */}
                    <div className="absolute bottom-[100px] right-[20%] flex flex-col items-center text-center z-10 group">
                        <div className="w-16 h-16 rounded-2xl bg-[#0a0a0a] border border-white/10 flex items-center justify-center shadow-2xl mb-4 group-hover:border-blue-500/50 transition-colors relative">
                            <Zap size={24} className="text-white/40 group-hover:text-blue-500 transition-colors" />
                            <div className="absolute -top-2 -right-2 bg-blue-500 text-black p-1 rounded-full"><Lock size={10} /></div>
                        </div>
                        <h4 className="text-blue-400 font-bold font-mono text-sm tracking-widest mb-1">02. CONTEXT</h4>
                        <p className="text-xs text-white/50 max-w-[150px]">The DNA.</p>
                    </div>

                    {/* Phase 3: ANTIBODY (Bottom Left - 7:00) */}
                    <div className="absolute bottom-[100px] left-[20%] flex flex-col items-center text-center z-10 group">
                        <div className="w-16 h-16 rounded-2xl bg-[#0a0a0a] border border-white/10 flex items-center justify-center shadow-2xl mb-4 group-hover:border-signal/50 transition-colors">
                            <Shield size={24} className="text-white/40 group-hover:text-signal transition-colors" />
                        </div>
                        <h4 className="text-signal font-bold font-mono text-sm tracking-widest mb-1">03. ANTIBODY</h4>
                        <p className="text-xs text-white/50 max-w-[150px]">The Filter.</p>
                    </div>

                    {/* Phase 4: COMPUTE (Left - 9:00) */}
                    <div className="absolute top-1/2 -translate-y-[100px] left-[5%] flex flex-col items-center text-center z-10 group">
                        <div className="w-16 h-16 rounded-2xl bg-[#0a0a0a] border border-white/10 flex items-center justify-center shadow-2xl mb-4 group-hover:border-purple-500/50 transition-colors">
                            <Globe size={24} className="text-white/40 group-hover:text-purple-400 transition-colors" />
                        </div>
                        <h4 className="text-purple-400 font-bold font-mono text-sm tracking-widest mb-1">04. COMPUTE</h4>
                        <p className="text-xs text-white/50 max-w-[150px]">Global Intelligence.</p>
                    </div>

                    {/* Phase 5: EDITOR (Top Left - 11:00) */}
                    <div className="absolute top-[100px] left-[20%] flex flex-col items-center text-center z-10 group">
                        <div className="w-16 h-16 rounded-2xl bg-[#0a0a0a] border border-white/10 flex items-center justify-center shadow-2xl mb-4 group-hover:border-white/50 transition-colors relative">
                            <Terminal size={24} className="text-white/40 group-hover:text-white transition-colors" />
                        </div>
                        <h4 className="text-white font-bold font-mono text-sm tracking-widest mb-1">05. EDITOR</h4>
                        <p className="text-xs text-white/50 max-w-[150px]">The Landing.</p>
                    </div>

                </div>

                {/* MOBILE FALLBACK (Linear Stack) */}
                <div className="w-full max-w-md mx-auto mb-32 md:hidden space-y-8 relative z-10 pl-8 border-l border-white/10">
                    <div className="relative">
                        <span className="absolute -left-[41px] top-0 w-5 h-5 rounded-full bg-white border-4 border-black" />
                        <h4 className="text-white font-bold">THE ORIGIN (You)</h4>
                        <p className="text-xs text-white/50">Attached: <span className="text-amber-500">Long-Term Memory</span></p>
                    </div>
                    <div className="relative">
                        <span className="absolute -left-[39px] top-0 w-3 h-3 rounded-full bg-white animate-pulse" />
                        <h4 className="text-white font-bold font-mono text-xs tracking-widest">0. INTENT (Spark)</h4>
                    </div>
                    <div className="relative">
                        <span className="absolute -left-[39px] top-0 w-3 h-3 rounded-full bg-neon" />
                        <h4 className="text-neon font-bold font-mono text-xs tracking-widest">1. AWARENESS</h4>
                    </div>
                    <div className="relative">
                        <span className="absolute -left-[39px] top-0 w-3 h-3 rounded-full bg-blue-500" />
                        <h4 className="text-blue-500 font-bold font-mono text-xs tracking-widest">2. CONTEXT</h4>
                    </div>
                    <div className="relative">
                        <span className="absolute -left-[39px] top-0 w-3 h-3 rounded-full bg-signal" />
                        <h4 className="text-signal font-bold font-mono text-xs tracking-widest">3. ANTIBODY</h4>
                    </div>
                    <div className="relative">
                        <span className="absolute -left-[39px] top-0 w-3 h-3 rounded-full bg-purple-500" />
                        <h4 className="text-purple-500 font-bold font-mono text-xs tracking-widest">4. COMPUTE</h4>
                    </div>
                    <div className="relative">
                        <span className="absolute -left-[39px] top-0 w-3 h-3 rounded-full bg-white" />
                        <h4 className="text-white font-bold font-mono text-xs tracking-widest">5. EDITOR</h4>
                        <p className="text-[10px] text-amber-500">Verify & Save.</p>
                    </div>
                </div>

                <div className="absolute left-[19px] md:left-1/2 top-32 bottom-0 w-px bg-white/5 md:-translate-x-1/2 hidden md:block" />

                <div className="absolute left-[19px] md:left-1/2 top-32 bottom-0 w-px bg-white/5 md:-translate-x-1/2 hidden md:block" />

                {/* STEP 0: INTENT (The Spark) - NEW */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16 relative items-stretch">
                    <div className="order-2 md:order-2 flex flex-col p-6 rounded-3xl bg-white/[0.02] border border-white/5 backdrop-blur-sm hover:bg-white/[0.04] transition-colors group/text">
                        <div className="inline-flex items-center gap-2 mb-4 opacity-50 group-hover/text:opacity-100 transition-opacity">
                            <span className="text-white font-mono text-xs font-bold tracking-widest">PHASE_00: INTENT</span>
                            <span className="h-px w-8 bg-white/50"></span>
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-4">Vector Initialization</h3>
                        <p className="text-white/70 text-lg leading-relaxed">
                            <b>"Thought" is a physical vector.</b> <br /><br />
                            We don't wait for your keystrokes to finish. Sidelith captures the <b>High-Dimensional Intent</b> of your request the moment it enters the buffer. <br /><br />
                            <i className="text-white/90">"Zero-Latency Perception."</i>
                        </p>
                    </div>
                    <div className="order-1 md:order-1">
                        <div className="h-full min-h-[220px] border border-white/10 rounded-2xl bg-[#0a0a0a] p-6 relative overflow-hidden group font-mono text-xs md:text-sm shadow-2xl hover:border-white/30 transition-colors">
                            <div className="absolute top-0 right-0 p-3 text-[11px] text-zinc-500 font-bold tracking-wider">BUFFER_ACTIVE</div>
                            <div className="space-y-4 pt-2">
                                <div className="flex items-center gap-4 text-white animate-pulse">
                                    <Sparkles size={16} />
                                    <span className="font-bold">CAPTURING INTENT_VECTOR...</span>
                                </div>
                                <div className="mt-4 p-3 bg-white/5 border border-white/10 rounded text-white/80">
                                    {`> origin: "User Request"`} <br />
                                    {`> velocity: 120ms (Typing Speed)`} <br />
                                    {`> target: "Refactor Auth Schema"`}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* STEP 1: THE AWARENESS (Scan & Forensics) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16 relative items-stretch">
                    <div className="md:text-right flex flex-col items-start md:items-end order-2 md:order-1 p-6 rounded-3xl bg-white/[0.02] border border-white/5 backdrop-blur-sm hover:bg-white/[0.04] transition-colors group/text">
                        <div className="inline-flex items-center gap-2 mb-4 opacity-50 group-hover/text:opacity-100 transition-opacity">
                            <span className="text-neon font-mono text-xs font-bold tracking-widest">PHASE_01: AWARENESS</span>
                            <span className="h-px w-8 bg-neon/50"></span>
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-4">The Fractal Scan</h3>
                        <p className="text-white/70 text-lg leading-relaxed">
                            <b>We map the territory.</b> <br /><br />
                            Sidelith doesn't just "read" files; it builds a cryptographic <b>Local Graph</b> of your repository. Every function, class, and variable is indexed by its <b>Merkle Hash</b>. <br /><br />
                            <i className="text-neon/90">"100% Codebase Awareness."</i>
                        </p>
                    </div>
                    <div className="order-1 md:order-2">
                        <div className="h-full min-h-[220px] border border-white/10 rounded-2xl bg-[#0a0a0a] p-6 relative overflow-hidden group font-mono text-xs md:text-sm shadow-2xl hover:border-neon/30 transition-colors">
                            <div className="absolute top-0 right-0 p-3 text-[11px] text-zinc-500 font-bold tracking-wider">MEM_MAP_ACTIVE</div>
                            <div className="space-y-4 pt-2">
                                <div className="grid grid-cols-[1fr_auto_auto] gap-4 text-zinc-400 border-b border-white/10 pb-2 text-[11px] font-bold tracking-wider">
                                    <span>NODE_ID</span>
                                    <span>HASH</span>
                                    <span>STATUS</span>
                                </div>
                                <div className="grid grid-cols-[1fr_auto_auto] gap-4 text-neon font-medium">
                                    <span>/core/auth.ts</span>
                                    <span className="opacity-80">0x7f...9a2b</span>
                                    <span>[MAPPED]</span>
                                </div>
                                <div className="mt-6 p-3 bg-neon/5 border border-neon/20 rounded text-neon text-xs md:text-sm font-medium">
                                    {`> scan_rate: 177,402 ops/s`} <br />
                                    {`> drift_detection: ENABLED`}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* STEP 2: THE CONTEXT (Inject) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16 relative items-stretch">
                    <div className="order-2 md:order-2 flex flex-col p-6 rounded-3xl bg-white/[0.02] border border-white/5 backdrop-blur-sm hover:bg-white/[0.04] transition-colors group/text">
                        <div className="inline-flex items-center gap-2 mb-4 opacity-50 group-hover/text:opacity-100 transition-opacity">
                            <span className="text-blue-500 font-mono text-xs font-bold tracking-widest">PHASE_02: CONTEXT</span>
                            <span className="h-px w-8 bg-blue-500/50"></span>
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-4">Entropy Reduction</h3>
                        <p className="text-white/70 text-lg leading-relaxed">
                            <b>We narrow the search space.</b> <br /><br />
                            Before the AI speaks, we perform a <b>Strategic Injection</b>. We force-feed the model the exact dependencies and constraints it needs, grounding every generation in your verified architectural reality. <br /><br />
                            <i className="text-blue-400">"Deterministic Context."</i>
                        </p>
                    </div>
                    <div className="order-1 md:order-1">
                        <div className="rounded-xl border border-white/10 bg-[#0a0a0a] shadow-2xl overflow-hidden group hover:border-blue-500/30 transition-colors">
                            <div className="h-10 bg-white/5 border-b border-white/5 flex items-center px-4 justify-between">
                                <span className="text-xs font-mono text-blue-400 uppercase font-bold tracking-wider">context_vector_v4.json</span>
                                <div className="flex gap-1.5">
                                    <div className="w-2 h-2 rounded-full bg-blue-500/50"></div>
                                    <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                                </div>
                            </div>
                            <div className="p-6 font-mono text-xs md:text-sm leading-relaxed overflow-x-auto text-white/90">
                                <pre>
                                    {`{
  "injection_id": "inj_99a8s7",
  "constraints": {
    "style": "SOLID_PRINCIPLES",
    "forbidden_patterns": ["GodClass"]
  }
}`}
                                </pre>
                            </div>
                        </div>
                    </div>
                </div>

                {/* STEP 3: THE ANTIBODY (Shield) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16 relative items-stretch">
                    <div className="md:text-right flex flex-col items-start md:items-end order-2 md:order-1 p-6 rounded-3xl bg-white/[0.02] border border-white/5 backdrop-blur-sm hover:bg-white/[0.04] transition-colors group/text">
                        <div className="inline-flex items-center gap-2 mb-4 opacity-50 group-hover/text:opacity-100 transition-opacity">
                            <span className="text-signal font-mono text-xs font-bold tracking-widest">PHASE_03: ANTIBODY</span>
                            <span className="h-px w-8 bg-signal/50"></span>
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-4">Data Sovereignty</h3>
                        <p className="text-white/70 text-lg leading-relaxed">
                            <b>The Gatekeeper.</b> <br /><br />
                            Your code is your IP. Our <b>Pulse Engine</b> acts as a pre-flight firewall, stripping secrets and enforcing corporate policy <i>before</i> any packet leaves your machine. <br /><br />
                            <i className="text-signal">"Compliance by Design."</i>
                        </p>
                    </div>
                    <div className="order-1 md:order-2">
                        <div className="rounded-xl border border-white/10 bg-[#0a0a0a] shadow-2xl overflow-hidden group hover:border-signal/30 transition-colors">
                            <div className="h-10 bg-white/5 border-b border-white/5 flex items-center px-4 justify-between">
                                <div className="flex items-center gap-2">
                                    <Shield size={14} className="text-zinc-400" />
                                    <span className="text-xs font-mono text-zinc-400 font-bold tracking-wider">pulse-guard — active</span>
                                </div>
                                <div className="w-2 h-2 rounded-full bg-signal animate-pulse" />
                            </div>
                            <div className="p-6 font-mono text-xs md:text-sm space-y-3">
                                <div className="text-zinc-500 border-b border-white/10 pb-2 mb-3 font-medium">
                                    [PULSE] Scanning Outbound Request...
                                </div>
                                <div className="grid grid-cols-[1fr_auto] gap-4 items-center">
                                    <span className="text-white font-medium">check(pii_leakage)</span>
                                    <span className="text-signal bg-signal/10 px-2 py-0.5 rounded font-bold">PASSED</span>
                                </div>
                                <div className="mt-4 pt-3 border-t border-white/10 text-signal font-bold tracking-wide">
                                    {`>> POLICY_CHECK: PASS [block_mode=active]`}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* STEP 4: GLOBAL INTELLIGENCE (Compute) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16 relative items-stretch">
                    <div className="order-2 md:order-2 flex flex-col p-6 rounded-3xl bg-white/[0.02] border border-white/5 backdrop-blur-sm hover:bg-white/[0.04] transition-colors group/text">
                        <div className="inline-flex items-center gap-2 mb-4 opacity-50 group-hover/text:opacity-100 transition-opacity">
                            <span className="text-purple-500 font-mono text-xs font-bold tracking-widest">PHASE_04: COMPUTE</span>
                            <span className="h-px w-8 bg-purple-500/50"></span>
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-4">The Global Mesh</h3>
                        <p className="text-white/70 text-lg leading-relaxed">
                            <b>Compound Reasoning.</b> <br /><br />
                            We don't send your code to the cloud. We query the cloud for <b>Anonymous Strategic Patterns</b>. Sidelith aggregates reasoning from multiple sovereign nodes to solve your specific local problem. <br /><br />
                            <i className="text-purple-400">"Global Wisdom, Local Data."</i>
                        </p>
                    </div>
                    <div className="order-1 md:order-1">
                        <div className="h-full min-h-[220px] border border-white/10 rounded-2xl bg-[#0a0a0a] p-6 relative overflow-hidden group font-mono text-xs md:text-sm shadow-2xl hover:border-purple-500/30 transition-colors">
                            <div className="absolute top-0 right-0 p-3 text-[11px] text-zinc-500 font-bold tracking-wider">ANON_MESH_ACTIVE</div>
                            <div className="space-y-4 pt-2">
                                <div className="flex items-center gap-4 text-purple-400 animate-pulse">
                                    <Globe size={16} />
                                    <span className="font-bold">AGGREGATING PATTERNS...</span>
                                </div>
                                <div className="mt-4 p-3 bg-purple-500/10 border border-purple-500/20 rounded text-purple-300">
                                    {`> source: "strategy_441.json"`} <br />
                                    {`> match_score: 0.941 (cosine)`}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* STEP 5: THE LANDING (Editor) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16 relative items-stretch">
                    <div className="md:text-right flex flex-col items-start md:items-end order-2 md:order-1 p-6 rounded-3xl bg-white/[0.02] border border-white/5 backdrop-blur-sm hover:bg-white/[0.04] transition-colors group/text">
                        <div className="inline-flex items-center gap-2 mb-4 opacity-50 group-hover/text:opacity-100 transition-opacity">
                            <span className="text-white font-mono text-xs font-bold tracking-widest">PHASE_05: EDITOR</span>
                            <span className="h-px w-8 bg-white/50"></span>
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-4">Verified Execution</h3>
                        <p className="text-white/70 text-lg leading-relaxed">
                            <b>The Safe Landing.</b> <br /><br />
                            The solution lands in your Editor (VS Code). This is not the end; it is the <b>Verification Step</b>. You apply the diff. You run the test. <br /><br />
                            <i className="text-white/90">"Trust, but Verify."</i>
                        </p>
                    </div>
                    <div className="order-1 md:order-2">
                        <div className="h-full min-h-[220px] border border-white/10 rounded-2xl bg-[#0a0a0a] p-6 relative overflow-hidden group font-mono text-xs md:text-sm shadow-2xl hover:border-white/30 transition-colors">
                            <div className="absolute top-0 right-0 p-3 text-[11px] text-zinc-500 font-bold tracking-wider">IDE_LINK_ACTIVE</div>
                            <div className="space-y-4 pt-2">
                                <div className="flex items-center gap-4 text-white">
                                    <Terminal size={16} />
                                    <span className="font-bold">APPLYING DIFF...</span>
                                </div>
                                <div className="mt-4 p-3 bg-white/5 border border-white/10 rounded text-white/80">
                                    {`+ verify_token_integrity(jwt)`} <br />
                                    {`- legacy_check(token)`}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* RESULT: LONG-TERM MEMORY */}
                <div className="text-center relative z-10">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-16 relative">
                        <div className="order-2 md:order-2 flex flex-col justify-center px-6">
                            <div className="inline-flex items-center gap-2 mb-4">
                                <span className="text-amber-500 font-mono text-xs font-bold tracking-widest">PHASE_06: MEMORY</span>
                                <span className="h-px w-8 bg-amber-500/50"></span>
                            </div>
                            <h3 className="text-2xl font-bold text-white mb-4">Long-Term Memory</h3>
                            <p className="text-white/60 text-lg leading-relaxed max-w-sm">
                                <b>The Infinite Loop.</b> <br /><br />
                                The verified solution is serialized into the <b>Chronos Vector Store</b> (`ledger.db`). This updates the <b>Neural Logic Graph</b>, ensuring <b>Phase 01 (Awareness)</b> indexes this pattern for future context resolution. <br /><br />
                                <i>"The Operator never forgets."</i>
                            </p>
                        </div>
                        <div className="order-1 md:order-1">
                            <div className="h-full min-h-[220px] border border-white/10 rounded-2xl bg-[#0a0a0a] p-6 relative overflow-hidden group font-mono text-xs md:text-sm shadow-2xl hover:border-amber-500/30 transition-colors">
                                <div className="absolute top-0 right-0 p-3 text-[11px] text-zinc-500 font-bold tracking-wider">CHRONOS_STORE_ACTIVE</div>
                                <div className="space-y-4 pt-2">
                                    <div className="flex items-center gap-4 text-amber-500">
                                        <Database size={16} />
                                        <span className="font-bold">SAVING PRECEDENT...</span>
                                    </div>
                                    <div className="mt-4 p-3 bg-amber-500/10 border border-amber-500/20 rounded text-amber-500/80">
                                        {`> type: "Strategic_Commit"`} <br />
                                        {`> action: "UPSERT_VECTOR_NODE"`}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </section>


            {/* 4. GOVERNANCE LAYER (Trust & Compliance) */}
            <section className="section-spacing w-full max-w-6xl px-6 mb-24 relative z-10">
                <div className="p-1 rounded-3xl bg-gradient-to-r from-transparent via-white/10 to-transparent">
                    <div className="bg-[#0a0a0a] rounded-[22px] border border-white/5 p-8 md:p-12 overflow-hidden relative">
                        {/* Background Splashes */}
                        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-emerald-500/5 blur-[100px] rounded-full pointer-events-none" />

                        <div className="flex flex-col md:flex-row items-center justify-between gap-12 relative z-10">

                            {/* Left: Text */}
                            <div className="text-center md:text-left max-w-lg">
                                <div className="inline-flex items-center gap-2 mb-4">
                                    <Shield size={16} className="text-emerald-500" />
                                    <span className="text-emerald-500 font-mono text-xs font-bold tracking-widest uppercase">The Governance Layer</span>
                                </div>
                                <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
                                    Built for the <span className="text-white/50">Paranoid</span>.
                                </h2>
                                <p className="text-lg text-white/60 leading-relaxed mb-8">
                                    We don't sell "Privacy Policies". We sell <b>Architecture</b>. <br />
                                    Sidelith is engineered to operate in hostile, regulated environments without modification.
                                </p>
                                <div className="flex flex-col md:flex-row gap-4 justify-center md:justify-start">
                                    <div className="flex items-center gap-2 text-xs font-mono text-white/40">
                                        <Check size={14} className="text-emerald-500" /> NO CLOUD RETENTION
                                    </div>
                                    <div className="flex items-center gap-2 text-xs font-mono text-white/40">
                                        <Check size={14} className="text-emerald-500" /> NO MODEL TRAINING
                                    </div>
                                </div>
                            </div>

                            {/* Right Wrapper: Badges + Disclosure */}
                            <div className="flex flex-col items-center md:items-end w-full md:w-auto">
                                <div className="grid grid-cols-2 gap-4 w-full md:w-auto">

                                    {/* Badge 1: AES-256 */}
                                    <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-emerald-500/30 transition-colors group text-center min-w-[160px]">
                                        <div className="w-10 h-10 mx-auto rounded-full bg-emerald-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                            <Lock size={18} className="text-emerald-400" />
                                        </div>
                                        <h4 className="text-white font-bold text-sm mb-1">AES-256 GCM</h4>
                                        <p className="text-[10px] text-white/40 uppercase tracking-wider font-mono">ENCRYPTION</p>
                                    </div>

                                    {/* Badge 2: HIPAA */}
                                    <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-blue-500/30 transition-colors group text-center min-w-[160px]">
                                        <div className="w-10 h-10 mx-auto rounded-full bg-blue-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                            <Activity size={18} className="text-blue-400" />
                                        </div>
                                        <h4 className="text-white font-bold text-sm mb-1">HIPAA</h4>
                                        <p className="text-[10px] text-white/40 uppercase tracking-wider font-mono">ELIGIBLE ARCH</p>
                                    </div>

                                    {/* Badge 3: SOC 2 */}
                                    <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-purple-500/30 transition-colors group text-center min-w-[160px]">
                                        <div className="w-10 h-10 mx-auto rounded-full bg-purple-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                            <Database size={18} className="text-purple-400" />
                                        </div>
                                        <h4 className="text-white font-bold text-sm mb-1">SOC 2 Type II</h4>
                                        <p className="text-[10px] text-white/40 uppercase tracking-wider font-mono">ALIGNED CONTROLS</p>
                                    </div>

                                    {/* Badge 4: GDPR */}
                                    <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-amber-500/30 transition-colors group text-center min-w-[160px]">
                                        <div className="w-10 h-10 mx-auto rounded-full bg-amber-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                                            <Globe size={18} className="text-amber-400" />
                                        </div>
                                        <h4 className="text-white font-bold text-sm mb-1">GDPR</h4>
                                        <p className="text-[10px] text-white/40 uppercase tracking-wider font-mono">ZERO RETENTION</p>
                                    </div>

                                </div>

                                {/* Disclosure Note */}
                                <div className="mt-4 text-center md:text-right max-w-[350px]">
                                    <p className="text-[10px] text-white/40 leading-relaxed font-mono">
                                        * Architecture verified internally. Independent third-party attestation (SOC 2 Type II) is scheduled for Q4 2026.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* 5. PRICING (Usage Based) */}
            <section className="section-spacing w-full max-w-6xl px-6">
                <div className="text-center mb-16">
                    <h2 className="text-h2 mb-4">Pay for Intelligence.</h2>
                    <p className="text-body-lg text-white/60">Scalable Side Units (SUs) for your semantic operations.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-2">
                    {/* Hobby */}
                    <div className="p-6 rounded-xl border border-white/5 bg-white/[0.01] hover:bg-white/[0.02] transition-colors flex flex-col h-full">
                        <div className="text-mono text-zinc-500 mb-4">Hobby</div>
                        <div className="text-h3 mb-1 text-white">$0 <span className="text-sm font-sans text-white/40">/ mo</span></div>
                        <div className="text-mono text-[10px] text-white/40 mb-6 tracking-wider">500 SUs / MO</div>
                        <p className="text-xs text-white/50 mb-6 min-h-[40px]">Perfect for individuals.</p>
                        <ul className="space-y-3 text-body text-white/60 mb-8 flex-grow">
                            <li className="flex gap-2 items-center"><Check size={14} className="text-white/20" /> Sovereign Pulse</li>
                            <li className="flex gap-2 items-center"><Check size={14} className="text-white/20" /> Fractal Memory</li>
                            <li className="flex gap-2 items-center"><Check size={14} className="text-white/20" /> Neural Logic Graph</li>
                        </ul>
                        <button className="w-full py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg font-medium text-sm transition-colors border border-white/5">Get Started</button>
                    </div>

                    {/* Pro */}
                    <div className="p-6 rounded-xl border border-blue-500/30 bg-blue-500/[0.03] relative overflow-hidden group flex flex-col h-full">
                        <div className="absolute top-0 right-0 px-3 py-1 bg-blue-500 text-[10px] font-bold text-white">POPULAR</div>
                        <div className="text-mono text-blue-400 mb-4">Pro</div>
                        <div className="text-h3 mb-1 text-white">$20 <span className="text-sm font-sans text-white/40">/ mo</span></div>
                        <div className="text-mono text-[10px] text-white/40 mb-6 tracking-wider">5,000 SUs / MO</div>
                        <p className="text-xs text-white/50 mb-6 min-h-[40px]">Standard for Professionals.</p>
                        <ul className="space-y-3 text-body text-white/80 mb-8 flex-grow">
                            <li className="flex gap-2 items-center"><Check size={14} className="text-blue-500" /> Sovereign Pulse</li>
                            <li className="flex gap-2 items-center"><Check size={14} className="text-blue-500" /> Fractal Memory</li>
                            <li className="flex gap-2 items-center"><Check size={14} className="text-blue-500" /> Neural Logic Graph</li>
                        </ul>
                        <button className="w-full py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-medium text-sm transition-colors shadow-lg shadow-blue-500/20">Get Started</button>
                    </div>

                    {/* Elite */}
                    <div className="p-6 rounded-xl border border-white/5 bg-white/[0.01] hover:bg-white/[0.02] transition-colors flex flex-col h-full">
                        <div className="text-mono text-zinc-500 mb-4">Elite</div>
                        <div className="text-h3 mb-1 text-white">$60 <span className="text-sm font-sans text-white/40">/ mo</span></div>
                        <div className="text-mono text-[10px] text-white/40 mb-6 tracking-wider">25,000 SUs / MO</div>
                        <p className="text-xs text-white/50 mb-6 min-h-[40px]">For Power Users.</p>
                        <ul className="space-y-3 text-body text-white/60 mb-8 flex-grow">
                            <li className="flex gap-2 items-center"><Check size={14} className="text-white/20" /> Sovereign Pulse</li>
                            <li className="flex gap-2 items-center"><Check size={14} className="text-white/20" /> Fractal Memory</li>
                            <li className="flex gap-2 items-center"><Check size={14} className="text-white/20" /> Neural Logic Graph</li>
                        </ul>
                        <button className="w-full py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg font-medium text-sm transition-colors border border-white/5">Get Started</button>
                    </div>

                    {/* High Tech */}
                    <div className="p-6 rounded-xl border border-purple-500/20 bg-purple-500/[0.02] hover:bg-purple-500/[0.04] transition-colors flex flex-col h-full">
                        <div className="text-mono text-purple-400 mb-4">High Tech</div>
                        <div className="text-h3 mb-1 text-white">Custom <span className="text-sm font-sans text-white/40"></span></div>
                        <div className="text-mono text-[10px] text-white/40 mb-6 tracking-wider">ABSOLUTE SOVEREIGNTY</div>
                        <p className="text-xs text-white/50 mb-6 min-h-[40px]">For IP-Sensitive Enterprises.</p>
                        <ul className="space-y-3 text-body text-white/60 mb-8 flex-grow">
                            <li className="flex gap-2 items-center"><Check size={14} className="text-purple-500" /> <b>Airgap Mode (Ollama, Azure & Custom)</b></li>
                            <li className="flex gap-2 items-center"><Check size={14} className="text-purple-500" /> Sovereign Pulse</li>
                            <li className="flex gap-2 items-center"><Check size={14} className="text-purple-500" /> Fractal Memory</li>
                            <li className="flex gap-2 items-center"><Check size={14} className="text-purple-500" /> Neural Logic Graph</li>
                        </ul>
                        <a href="mailto:hq@sidelith.com" className="w-full py-2 bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 rounded-lg font-medium text-sm transition-colors border border-purple-500/20 flex items-center justify-center">Contact Sales</a>
                    </div>
                </div>

                {/* Add-on: Structural Refills */}
                <div className="mt-4 p-4 rounded-xl border border-white/5 bg-white/[0.01] flex flex-col md:flex-row items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <div className="p-2 rounded-lg bg-orange-500/10 border border-orange-500/20">
                            <Zap className="w-5 h-5 text-orange-400" />
                        </div>
                        <div>
                            <h4 className="text-sm font-bold text-white uppercase tracking-wider">Structural Refills</h4>
                            <p className="text-xs text-white/50">Ran out of throughput? Add capacity incrementally.</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-6">
                        <div className="text-right">
                            <div className="text-xl font-bold text-white">$10</div>
                            <div className="text-[10px] text-white/40 uppercase tracking-wider">250 Extra SUs</div>
                        </div>
                        <button className="px-6 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-white font-medium text-xs transition-colors border border-white/5">
                            Get Started
                        </button>
                    </div>
                </div>
            </section>

            {/* 6. INSTALLATION (The Developer's Shortcut) */}
            <section className="section-spacing w-full max-w-4xl px-6 text-center mb-32">
                <div className="mb-12">
                    <h2 className="text-hero mb-6 text-white leading-tight">
                        Ready to <span className="text-emerald-400">Deploy?</span>
                    </h2>
                    <p className="text-body-lg text-white/60 max-w-2xl mx-auto mb-12">
                        You don't need a heavy account. You need a binary. <br />
                        <span className="text-white">The Developer's Shortcut</span> starts here.
                    </p>
                </div>

                <InstallWidget />


            </section>

            {/* 5. FOOTER */}
            <footer className="w-full border-t border-white/5 py-12">
                <div className="max-w-6xl mx-auto px-6 flex justify-between items-center text-xs text-white/30 font-mono">
                    <div className="flex gap-4">
                        <span className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-emerald-500/50" /> All Systems Operational</span>
                        <span>Memory: 148MB Used</span>
                    </div>
                    <div>
                        "Intelligence means being able to survive the user's mistakes."
                    </div>
                </div>
            </footer>

            {/* Background Grid */}
            <div className="fixed inset-0 z-0 pointer-events-none bg-grid-pattern opacity-20" />
        </main>
    );
}
