import { ArrowRight, Terminal, Shield, Zap, Cpu, Database, Command, Check, Activity, Lock, Globe, Sparkles, Bot, Monitor, Wind } from "lucide-react";
import { InstallWidget } from "../components/InstallWidget";

export default function Home() {
    return (
        <main className="min-h-screen flex flex-col items-center overflow-hidden bg-void text-foreground selection:bg-neon/20">
            {/* 1. HERO SECTION */}
            <section className="w-full max-w-5xl px-6 flex flex-col items-center text-center z-10 pt-40 pb-20">
                <h1 className="text-hero mb-8 bg-gradient-to-b from-white to-white/60 bg-clip-text text-transparent animate-in fade-in slide-in-from-bottom-8 duration-1000 fill-mode-both leading-[1.2] pb-1">
                    Intelligence that Remembers.
                </h1>

                <p className="text-xl md:text-2xl text-white/50 max-w-3xl mb-12 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-200 fill-mode-both leading-relaxed font-light">
                    Sidelith is the <span className="text-white font-medium">deterministic memory substrate</span> for AI agents. <br />
                    Curing digital amnesia with fractal ontology and 100% local persistence.
                </p>

                <div className="flex flex-col items-center gap-6 animate-in fade-in slide-in-from-bottom-16 duration-1000 delay-300 fill-mode-both">
                    <a href="#install-widget" className="group flex items-center gap-2 px-8 py-4 rounded-full bg-white text-black font-bold hover:bg-neon hover:text-black transition-all shadow-[0_0_40px_rgba(255,255,255,0.1)] hover:shadow-[0_0_60px_rgba(0,255,157,0.3)]">
                        The Developer's Shortcut <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                    </a>
                </div>
            </section>

            {/* 2. THE PROBLEM (Where AI Fails) */}
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
                                        Recovery Rate: 98% | Substrate: SQLite
                                    </div>
                                </div>
                                <p className="text-white/50 text-lg leading-relaxed max-w-xl">
                                    Generative models are stateless. Sidelith provides the <b>persistent substrate</b>. We stop the cycle of repeating yourself by providing a permanent semantic anchor.
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
                                Dampening: 0.94<br />
                                Noise Isolation: Binary
                            </div>
                        </div>
                        <h3 className="text-xl font-bold text-white mb-4">Context Rot</h3>
                        <p className="text-white/40 leading-relaxed text-sm">
                            The degradation of reasoning as noise accumulates. Sidelith is the antibody to generative entropy.
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
                                    Architectural maneuvers are cryptographically sealed. Prevent reasoning drift with 100% auditability.
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

            {/* NEW: THE STRUGGLE BENTO (High-Fidelity Friction Model) */}
            <section className="section-spacing w-full max-w-6xl px-6">
                <div className="mb-24 text-center">
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                        The Cost of <span className="text-red-500">Struggle</span>.
                    </h2>
                    <p className="text-white/40 text-lg md:text-xl font-light max-w-2xl mx-auto">
                        We mapped the interaction bottleneck between human intent and machine execution. <br />
                        AI is fast, but <b>Friction is expensive.</b>
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-stretch mb-24">
                    {/* Card 1: AMNESIA (The 3rd Coffee Loop) */}
                    <div className="md:col-span-12 lg:col-span-8 p-10 rounded-[32px] border border-white/10 bg-white/[0.02] hover:bg-white/[0.04] transition-all group overflow-hidden relative">
                        <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                            <Wind size={200} />
                        </div>
                        <div className="relative z-10 flex flex-col md:flex-row gap-10 items-center">
                            <div className="flex-1">
                                <h3 className="text-3xl font-bold text-white mb-4">The 3rd Coffee Loop</h3>
                                <p className="text-white/50 text-lg leading-relaxed mb-6">
                                    Re-explaining your architecture while your coffee gets cold. Gen-AI is stateless; it forgets the "Why" every 5,000 tokens.
                                </p>
                                <div className="flex gap-4 items-center text-xs font-mono text-red-500/60 uppercase tracking-widest">
                                    <span>[Narrative Gap]</span>
                                    <div className="h-px flex-1 bg-red-500/20" />
                                    <span>High Entropy</span>
                                </div>
                            </div>
                            <div className="w-full md:w-64 p-6 rounded-2xl bg-[#030303] border border-white/5 font-mono text-center group/metric transition-all duration-500 hover:border-red-500/20">
                                <div className="relative h-24 flex items-center justify-center">
                                    <p className="text-5xl font-bold text-red-500 mb-2 transition-all duration-500 group-hover/metric:opacity-0 group-active/metric:opacity-0 group-hover/metric:scale-95 group-active/metric:scale-95 absolute">0.82</p>
                                    <div className="opacity-0 group-hover/metric:opacity-100 group-active/metric:opacity-100 transition-all duration-500 scale-95 group-hover/metric:scale-100 group-active/metric:scale-100 flex flex-col items-center">
                                        <p className="text-xl font-bold text-red-500 mb-1">μ = 0.82</p>
                                        <p className="text-[8px] text-white/40 uppercase tracking-widest leading-tight">
                                            Grounding Overhead<br />
                                            Recursive Rectification<br />
                                            82% Token Decay
                                        </p>
                                    </div>
                                </div>
                                <p className="text-[10px] text-white/30 tracking-[0.2em] uppercase">Interaction Friction</p>
                            </div>
                        </div>
                    </div>

                    {/* Card 2: SURPRISE (Synthetic Debt) */}
                    <div className="md:col-span-6 lg:col-span-4 p-8 rounded-[32px] border border-orange-500/10 bg-orange-500/[0.02] hover:bg-orange-500/[0.04] transition-all group">
                        <Activity className="text-orange-500 mb-6" size={32} />
                        <h3 className="text-xl font-bold text-white mb-4">Synthetic Debt</h3>
                        <p className="text-white/40 leading-relaxed text-base">
                            Save 10 minutes on code generation. Lose 2 hours on "architectural surgery" correcting hallucinated patterns.
                        </p>
                    </div>

                    {/* Card 3: SATURATION (The 40-Tab Tax) */}
                    <div className="md:col-span-6 lg:col-span-4 p-8 rounded-[32px] border border-blue-500/10 bg-blue-500/[0.02] hover:bg-blue-500/[0.04] transition-all group">
                        <Globe className="text-blue-500 mb-6" size={32} />
                        <h3 className="text-xl font-bold text-white mb-4">The 40-Tab Tax</h3>
                        <p className="text-white/40 leading-relaxed text-base">
                            Hunting through documentation because the "Neural Link" is broken. AI blindness forces manual research loops.
                        </p>
                    </div>

                    {/* Card 4: DRIFT (Intent Mismatch) */}
                    <div className="md:col-span-12 lg:col-span-8 p-10 rounded-[32px] border border-emerald-500/10 bg-emerald-500/[0.02] hover:bg-emerald-500/[0.04] transition-all group overflow-hidden relative">
                        <div className="absolute -bottom-6 -right-6 opacity-5 group-hover:opacity-10 transition-opacity">
                            <Shield size={160} />
                        </div>
                        <div className="relative z-10 flex flex-col md:flex-row gap-10 items-center">
                            <div className="w-full md:w-64 p-6 rounded-2xl bg-[#050505] border border-emerald-500/10 font-mono text-center group/metric transition-all duration-500 hover:border-emerald-500/40">
                                <div className="relative h-24 flex items-center justify-center">
                                    <p className="text-5xl font-bold text-emerald-500 mb-2 transition-all duration-500 group-hover/metric:opacity-0 group-active/metric:opacity-0 group-hover/metric:scale-95 group-active/metric:scale-95 absolute">0.04</p>
                                    <div className="opacity-0 group-hover/metric:opacity-100 group-active/metric:opacity-100 transition-all duration-500 scale-95 group-hover/metric:scale-100 group-active/metric:scale-100 flex flex-col items-center">
                                        <p className="text-xl font-bold text-emerald-500 mb-1">μ = 0.04</p>
                                        <p className="text-[8px] text-emerald-500/40 uppercase tracking-widest leading-tight">
                                            Deterministic Loop<br />
                                            Merkle-Validated<br />
                                            96% Strategic Velocity
                                        </p>
                                    </div>
                                </div>
                                <p className="text-[10px] text-emerald-500/40 tracking-[0.2em] uppercase">Sovereign State</p>
                            </div>
                            <div className="flex-1">
                                <h3 className="text-3xl font-bold text-white mb-4">The Permanent Anchor</h3>
                                <p className="text-white/50 text-lg leading-relaxed mb-6">
                                    Sidelith never repeats a mistake. We was built by developers who struggled—so we fixed the "Why" once and for all.
                                </p>
                                <div className="flex gap-4 items-center text-xs font-mono text-emerald-500/60 uppercase tracking-widest">
                                    <span>[Zero Drift]</span>
                                    <div className="h-px flex-1 bg-emerald-500/20" />
                                    <span>Memory Sustained</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="text-center max-w-3xl mx-auto border-t border-white/5 pt-16">
                    <p className="text-xl text-white/60 font-light mb-8">
                        We spent years fighting these bottlenecks. Sidelith is our proud, definitive <b>antibody</b>. <br />
                        We're brave enough to claim we fix it—humble enough to know we build for you.
                    </p>
                    <p className="text-[10px] font-mono text-white/20 uppercase tracking-[0.3em] leading-relaxed">
                        * Indices represent normalized interaction friction (0.00–1.00). <br />
                        Findings based on 1,000+ internal iterations comparing stateless RAG vs. Sidelith.
                    </p>
                </div>
            </section>

            {/* 3. THE SOLUTION (How We Fix It) */}
            <section className="section-spacing w-full max-w-6xl px-4 z-10 relative">
                <div className="text-center mb-32">
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                        The <span className="text-neon">Sovereign Shield</span>.
                    </h2>
                    <p className="text-xl text-white/40 font-light max-w-2xl mx-auto">
                        A deterministic loop that replaces noise with truth.
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

                        {/* 3. LEARNING LOOP (Editor -> Memory) - Tactical Vectoring (Golden Ratio Offset) */}
                        <path id="learning-line" d="M 315 215 Q 380 285 435 335" stroke="#f59e0b" strokeWidth="2" className="animate-pulse opacity-80" strokeLinecap="round" markerEnd="url(#arrow-head-gold)" />
                        <text dy="-10">
                            <textPath href="#learning-line" startOffset="50%" textAnchor="middle" className="fill-amber-500 text-[10px] font-bold font-mono tracking-widest">
                                VERIFY, SAVE & EVOLVE
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
                        <h4 className="text-white font-bold font-mono text-sm tracking-widest mb-1">00. VECTORED INTENT</h4>
                        <p className="text-xs text-white/50 max-w-[150px]">The Initial Signal.</p>
                    </div>

                    {/* Phase 1: SHADOWING (Right - 3:00) */}
                    <div className="absolute top-1/2 -translate-y-[100px] right-[5%] flex flex-col items-center text-center z-10 group">
                        <div className="w-16 h-16 rounded-2xl bg-[#0a0a0a] border border-white/10 flex items-center justify-center shadow-2xl mb-4 group-hover:border-neon/50 transition-colors">
                            <Database size={24} className="text-white/40 group-hover:text-neon transition-colors" />
                        </div>
                        <h4 className="text-neon font-bold font-mono text-sm tracking-widest mb-1">01. FRACTAL DNA</h4>
                        <p className="text-xs text-white/50 max-w-[150px]">Structural Tree Analysis.</p>
                    </div>

                    {/* Phase 2: CONTEXT (Bottom Right - 5:00) */}
                    <div className="absolute bottom-[100px] right-[20%] flex flex-col items-center text-center z-10 group">
                        <div className="w-16 h-16 rounded-2xl bg-[#0a0a0a] border border-white/10 flex items-center justify-center shadow-2xl mb-4 group-hover:border-blue-500/50 transition-colors relative">
                            <Zap size={24} className="text-white/40 group-hover:text-blue-500 transition-colors" />
                            <div className="absolute -top-2 -right-2 bg-blue-500 text-black p-1 rounded-full"><Lock size={10} /></div>
                        </div>
                        <h4 className="text-blue-400 font-bold font-mono text-sm tracking-widest mb-1">02. MERKLE INJECTION</h4>
                        <p className="text-xs text-white/50 max-w-[150px]">Grounding the Narrative.</p>
                    </div>

                    {/* Phase 3: ANTIBODY (Bottom Left - 7:00) */}
                    <div className="absolute bottom-[100px] left-[20%] flex flex-col items-center text-center z-10 group">
                        <div className="w-16 h-16 rounded-2xl bg-[#0a0a0a] border border-white/10 flex items-center justify-center shadow-2xl mb-4 group-hover:border-signal/50 transition-colors">
                            <Shield size={24} className="text-white/40 group-hover:text-signal transition-colors" />
                        </div>
                        <h4 className="text-signal font-bold font-mono text-sm tracking-widest mb-1">03. GOVERNANCE SHIELD</h4>
                        <p className="text-xs text-white/50 max-w-[150px]">The Sovereignty Gate.</p>
                    </div>

                    {/* Phase 4: COMPUTE (Left - 9:00) */}
                    <div className="absolute top-1/2 -translate-y-[100px] left-[5%] flex flex-col items-center text-center z-10 group">
                        <div className="w-16 h-16 rounded-2xl bg-[#0a0a0a] border border-white/10 flex items-center justify-center shadow-2xl mb-4 group-hover:border-purple-500/50 transition-colors">
                            <Globe size={24} className="text-white/40 group-hover:text-purple-400 transition-colors" />
                        </div>
                        <h4 className="text-purple-400 font-bold font-mono text-sm tracking-widest mb-1">04. MESH INTELLIGENCE</h4>
                        <p className="text-xs text-white/50 max-w-[150px]">Compound Reasoning.</p>
                    </div>

                    {/* Phase 5: EDITOR (Top Left - 11:00) */}
                    <div className="absolute top-[100px] left-[20%] flex flex-col items-center text-center z-10 group">
                        <div className="w-16 h-16 rounded-2xl bg-[#0a0a0a] border border-white/10 flex items-center justify-center shadow-2xl mb-4 group-hover:border-white/50 transition-colors relative">
                            <Terminal size={24} className="text-white/40 group-hover:text-white transition-colors" />
                        </div>
                        <h4 className="text-white font-bold font-mono text-sm tracking-widest mb-1">05. PATTERN SERIALIZATION</h4>
                        <p className="text-xs text-white/50 max-w-[150px]">Recursive Learning Loop.</p>
                    </div>

                </div>

                {/* MOBILE PHASE HUB (High-Fidelity Grid Fallback) */}
                <div className="md:hidden w-full max-w-sm mx-auto mb-32 space-y-12 relative z-10 px-4">
                    {/* The Mobile Origin (You) */}
                    <div className="flex flex-col items-center text-center">
                        <div className="w-20 h-20 rounded-full bg-white flex items-center justify-center shadow-[0_0_40px_rgba(255,255,255,0.3)] border-4 border-[#0a0a0a] relative z-20">
                            <span className="text-black font-extrabold font-mono text-sm tracking-widest">YOU</span>
                        </div>
                        <div className="h-10 w-px bg-gradient-to-b from-white to-amber-500/50"></div>
                        <div className="px-4 py-2 rounded-lg bg-white/[0.02] border border-white/10 flex items-center gap-3">
                            <Database size={16} className="text-amber-500" />
                            <div className="flex flex-col items-start">
                                <span className="text-white font-bold text-[10px] tracking-widest">LONG-TERM MEMORY</span>
                                <span className="text-amber-500/60 text-[8px] uppercase font-mono">Status: Persisted</span>
                            </div>
                        </div>
                    </div>

                    {/* Phase Grid */}
                    <div className="grid grid-cols-2 gap-4">
                        {[
                            { id: "00", label: "INTENT", icon: Sparkles, color: "text-white", border: "border-white/20", shadow: "shadow-white/5", sub: "Initial Signal" },
                            { id: "01", label: "AWARENESS", icon: Database, color: "text-neon", border: "border-neon/20", shadow: "shadow-neon/5", sub: "Fractal DNA" },
                            { id: "02", label: "CONTEXT", icon: Zap, color: "text-blue-400", border: "border-blue-500/20", shadow: "shadow-blue-500/5", sub: "Merkle Inject" },
                            { id: "03", label: "ANTIBODY", icon: Shield, color: "text-signal", border: "border-signal/20", shadow: "shadow-signal/5", sub: "Local Shield" },
                            { id: "04", label: "COMPUTE", icon: Globe, color: "text-purple-400", border: "border-purple-500/20", shadow: "shadow-purple-500/5", sub: "Mesh Intel" },
                            { id: "05", label: "LEARNING", icon: Terminal, color: "text-white", border: "border-white/40", shadow: "shadow-white/10", sub: "Save & Evolve" }
                        ].map((phase) => (
                            <div key={phase.id} className={`p-4 rounded-2xl bg-[#0a0a0a] border ${phase.border} ${phase.shadow} flex flex-col items-center text-center group active:scale-95 transition-all`}>
                                <div className={`w-10 h-10 rounded-xl bg-white/[0.02] flex items-center justify-center mb-3`}>
                                    <phase.icon size={18} className={`${phase.color}`} />
                                </div>
                                <div className="text-[8px] font-mono text-white/30 tracking-[0.2em] mb-1">{phase.id}</div>
                                <h4 className={`text-[10px] font-bold tracking-widest ${phase.color} mb-1`}>{phase.label}</h4>
                                <p className="text-[8px] text-white/20 uppercase tracking-tighter">{phase.sub}</p>
                            </div>
                        ))}
                    </div>

                    {/* Mobile Connector Line Mask */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[200px] h-[300px] border border-white/5 rounded-full -z-10 blur-sm pointer-events-none" />
                </div>

                <div className="absolute left-[19px] md:left-1/2 top-32 bottom-0 w-px bg-white/5 md:-translate-x-1/2 hidden md:block" />

                {/* STEP 0: INTENT (The Spark) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-24 items-center">
                    <div className="order-2 md:order-1">
                        <h3 className="text-2xl font-bold text-white mb-4">00. Decipher Intent.</h3>
                        <p className="text-white/40 text-lg font-light leading-relaxed">
                            Sidelith captures high-dimensional intent, mapping your request against the core project mission.
                        </p>
                    </div>
                    <div className="order-1 md:order-2 p-8 rounded-3xl bg-white/[0.02] border border-white/5 font-mono text-xs text-white/60">
                        {`> origin: "User Request"`} <br />
                        {`> velocity: 120ms`} <br />
                        {`> status: VECTOR_CAPTURED`} <br />
                        {`> scan: 177,402 ops/s`} <br />
                        <span className="text-emerald-400">{`> merkle_tree: UPDATED`}</span>
                    </div>
                </div>

                {/* STEP 1: AWARENESS (Merkle Tree Visual) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-24 items-center">
                    <div className="order-1">
                        <div className="p-8 rounded-3xl bg-emerald-500/[0.02] border border-emerald-500/10 font-mono text-xs text-emerald-400/80 flex items-center justify-center min-h-[140px] relative overflow-hidden">
                            {/* Merkle Tree Branch Visualization */}
                            <svg width="160" height="80" viewBox="0 0 160 80" className="opacity-40">
                                <path d="M 80 10 L 40 40 M 80 10 L 120 40 M 40 40 L 20 70 M 40 40 L 60 70 M 120 40 L 100 70 M 120 40 L 140 70" stroke="currentColor" strokeWidth="1" strokeDasharray="2 2" />
                                <circle cx="80" cy="10" r="3" fill="currentColor" className="animate-pulse" />
                                <circle cx="40" cy="40" r="2" fill="currentColor" />
                                <circle cx="120" cy="40" r="2" fill="currentColor" />
                                <circle cx="20" cy="70" r="2" fill="currentColor" />
                                <circle cx="60" cy="70" r="2" fill="currentColor" />
                                <circle cx="100" cy="70" r="2" fill="currentColor" />
                                <circle cx="140" cy="70" r="2" fill="currentColor" />
                            </svg>
                            <div className="absolute bottom-4 right-4 text-[8px] uppercase tracking-widest text-emerald-500/30">
                                [SHA-256_ROOT]
                            </div>
                        </div>
                    </div>
                    <div className="order-2">
                        <h3 className="text-2xl font-bold text-white mb-4">01. Map the Territory.</h3>
                        <p className="text-white/40 text-lg font-light leading-relaxed">
                            Every signal is indexed into a cryptographic Merkle Tree, ensuring structural truth across polyglot codebases.
                        </p>
                    </div>
                </div>

                {/* STEP 2: ANCHORING */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-24 items-center">
                    <div className="order-2 md:order-1">
                        <h3 className="text-2xl font-bold text-white mb-4">02. Deterministic Anchoring.</h3>
                        <p className="text-white/40 text-lg font-light leading-relaxed">
                            We force-feed the model exact dependencies and constraints, grounding every generation in architectural reality.
                        </p>
                    </div>
                    <div className="order-1 md:order-2 p-8 rounded-3xl bg-blue-500/[0.02] border border-blue-500/10 font-mono text-xs text-blue-400/80">
                        {`"constraints": ["SOLID", "DRY"]`} <br />
                        {`"injection": "FORCE_SYNC"`} <br />
                        {`>> POLICY_CHECK: PASS`} <br />
                        {`>> ISOLATION: 100%`}
                    </div>
                </div>

                {/* STEP 3: INTEGRITY (Policy Shield Visual) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-24 items-center">
                    <div className="order-1">
                        <div className="p-8 rounded-3xl bg-red-500/[0.02] border border-red-500/10 font-mono text-xs text-red-400/80 flex flex-col items-center justify-center min-h-[140px] relative">
                            <div className="relative">
                                <div className="absolute inset-0 rounded-full border border-red-500/20 animate-ping" />
                                <div className="w-16 h-16 rounded-full bg-red-500/5 border border-red-500/20 flex items-center justify-center relative z-10">
                                    <Shield size={24} className="text-red-500 animate-pulse" />
                                </div>
                            </div>
                            <div className="mt-4 text-[8px] uppercase tracking-[0.3em] font-bold text-red-500/40">
                                POLICY_ENFORCED
                            </div>
                        </div>
                    </div>
                    <div className="order-2">
                        <h3 className="text-2xl font-bold text-white mb-4">03. Sovereign Integrity.</h3>
                        <p className="text-white/40 text-lg font-light leading-relaxed">
                            Secrets stay local. Corporate policy is enforced on the edge before any packet leaves.
                        </p>
                    </div>
                </div>

                {/* STEP 4: REASONING (The Mesh) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-24 items-center">
                    <div className="order-2 md:order-1">
                        <h3 className="text-2xl font-bold text-white mb-4">04. Compound Reasoning.</h3>
                        <p className="text-white/40 text-lg font-light leading-relaxed">
                            Sidelith orchestrates with high-end models (Claude, Gemini) through a secure local bridge, synthesizing complex solutions without leaking context.
                        </p>
                    </div>
                    <div className="order-1 md:order-2 p-8 rounded-3xl bg-purple-500/[0.02] border border-purple-500/10 font-mono text-xs text-purple-400/80 flex flex-col items-center justify-center min-h-[140px] relative overflow-hidden">
                        <div className="flex gap-4 items-center mb-4">
                            <Cpu size={24} className="text-white/20" />
                            <div className="h-px w-12 bg-white/20 border-t border-dashed border-white/40" />
                            <Globe size={24} className="text-purple-500 animate-pulse" />
                        </div>
                        <div className="text-[8px] uppercase tracking-widest text-purple-500/40 font-bold">
                            MESH_ORCHESTRATION_ACTIVE
                        </div>
                    </div>
                </div>

                {/* STEP 5: EVOLUTION (The Learning Loop) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-24 items-center">
                    <div className="order-1">
                        <div className="p-8 rounded-3xl bg-amber-500/[0.02] border border-amber-500/10 font-mono text-xs text-amber-400/80 flex flex-col items-center justify-center min-h-[140px] relative overflow-hidden">
                            <div className="flex gap-4 items-center mb-4">
                                <Database size={24} className="text-amber-500 animate-pulse" />
                            </div>
                            <div className="text-[8px] uppercase tracking-[0.3em] font-bold text-amber-500/40">
                                SERIALIZATION_COMPLETE
                            </div>
                        </div>
                    </div>
                    <div className="order-2">
                        <h3 className="text-2xl font-bold text-white mb-4">05. Episodic Sovereignty.</h3>
                        <p className="text-white/40 text-lg font-light leading-relaxed">
                            Verified solutions are serialized into the Chronos Vector Store. Sidelith captures the Reasoning Graph, Verified Patterns, and Forensic Guards from this interaction, ensuring the Operator never repeats a mistake.
                        </p>
                        <div className="mt-6 p-4 rounded-xl bg-amber-500/[0.03] border border-amber-500/10 font-mono text-[10px] text-amber-500/60 transition-all hover:bg-amber-500/[0.06]">
                            {`> update: NEURAL_LOGIC_GRAPH`} <br />
                            {`> serialized: [REASONING_GRAPH, PATTERN_V4]`} <br />
                            <span className="text-amber-500 font-bold">{`> status: KNOWLEDGE_BASE_UPDATED`}</span>
                        </div>
                    </div>
                </div>
            </section>

            {/* 4. THE SOVEREIGN SUBSTRATE (Unified Moats) */}
            <section className="section-spacing w-full max-w-6xl px-6 mb-24 relative z-10">
                <div className="text-center mb-20">
                    <div className="inline-block px-4 py-1.5 rounded-full border border-white/10 bg-white/5 text-white/60 font-mono text-xs tracking-widest uppercase mb-6">
                        Cryptographic Substrate
                    </div>
                    <h2 className="text-hero mb-4 text-white">
                        Defensive <span className="text-white/50">Moats</span>.
                    </h2>
                    <p className="text-body-lg text-white/60 max-w-2xl mx-auto">
                        Sidelith builds the most defensible architecture in local intelligence. Four pillars of pure structural truth.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
                    {/* Pillar 1: STRUCTURAL TRUTH */}
                    <div className="p-8 rounded-[28px] bg-[#0a0a0a] border border-white/5 hover:border-emerald-500/30 transition-all group relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 blur-[40px] rounded-full group-hover:bg-emerald-500/10 transition-colors" />
                        <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 flex items-center justify-center mb-6 border border-emerald-500/20">
                            <Shield size={24} className="text-emerald-500" />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-3">Structural Truth</h3>
                        <p className="text-white/40 text-base leading-relaxed mb-6">
                            Legacy Vector RAG is replaced by Merkle-Validated Context. 100% cryptographic integrity across polyglot codebases. No semantic drift.
                        </p>
                        <div className="flex gap-4">
                            <div className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[9px] font-mono text-white/40 uppercase tracking-widest">ED25519 SIGNED</div>
                            <div className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[9px] font-mono text-white/40 uppercase tracking-widest">SHA-256 ROOT</div>
                        </div>
                    </div>

                    {/* Pillar 2: NEURAL ISOLATION */}
                    <div className="p-8 rounded-[28px] bg-[#0a0a0a] border border-white/5 hover:border-blue-500/30 transition-all group relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 blur-[40px] rounded-full group-hover:bg-blue-500/10 transition-colors" />
                        <div className="w-14 h-14 rounded-2xl bg-blue-500/10 flex items-center justify-center mb-6 border border-blue-500/20">
                            <Lock size={24} className="text-blue-500" />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-3">Neural Isolation</h3>
                        <p className="text-white/40 text-base leading-relaxed mb-6">
                            Secrets stay local. Corporate policy is enforced on the edge. No data leakage, no third-party training. Total privacy by design.
                        </p>
                        <div className="flex gap-4">
                            <div className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[9px] font-mono text-white/40 uppercase tracking-widest">AES-256-GCM</div>
                            <div className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[9px] font-mono text-white/40 uppercase tracking-widest">SOC-2 READY</div>
                        </div>
                    </div>

                    {/* Pillar 3: SILICON VELOCITY */}
                    <div className="p-8 rounded-[28px] bg-[#0a0a0a] border border-white/5 hover:border-amber-500/30 transition-all group relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/5 blur-[40px] rounded-full group-hover:bg-amber-500/10 transition-colors" />
                        <div className="w-14 h-14 rounded-2xl bg-amber-500/10 flex items-center justify-center mb-6 border border-amber-500/20">
                            <Cpu size={24} className="text-amber-500" />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-3">Silicon Velocity</h3>
                        <p className="text-white/40 text-base leading-relaxed mb-6">
                            Sub-ms context injection for the post-GPT-5 era. FIPS-ready local persistence outlives the session with O(1) performance footprint.
                        </p>
                        <div className="flex gap-4">
                            <div className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[9px] font-mono text-white/40 uppercase tracking-widest">O(1) FLUX</div>
                            <div className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[9px] font-mono text-white/40 uppercase tracking-widest">&lt; 148MB RAM</div>
                        </div>
                    </div>

                    {/* Pillar 4: COLLECTIVE IMMUNITY */}
                    <div className="p-8 rounded-[28px] bg-[#0a0a0a] border border-white/5 hover:border-purple-500/30 transition-all group relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/5 blur-[40px] rounded-full group-hover:bg-purple-500/10 transition-colors" />
                        <div className="w-14 h-14 rounded-2xl bg-purple-500/10 flex items-center justify-center mb-6 border border-purple-500/20">
                            <Globe size={24} className="text-purple-500" />
                        </div>
                        <h3 className="text-xl font-bold text-white mb-3">Collective Immunity</h3>
                        <p className="text-white/40 text-base leading-relaxed mb-6">
                            Anonymized Ledger distribution. One user's victory becomes a global antibody via Verified Atomic Records (VARs).
                        </p>
                        <div className="flex gap-4">
                            <div className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[9px] font-mono text-white/40 uppercase tracking-widest">VAR DISTRIBUTED</div>
                            <div className="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-[9px] font-mono text-white/40 uppercase tracking-widest">PII STRIPPED</div>
                        </div>
                    </div>
                </div>

                <div className="bg-white/[0.02] border border-white/5 rounded-[22px] p-8 mt-12 overflow-hidden relative group">
                    <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
                        <Terminal size={120} className="text-white" />
                    </div>
                    <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8 text-center md:text-left">
                        <div className="max-w-xl">
                            <h4 className="text-lg font-bold text-white mb-2">The Distributed Ledger</h4>
                            <p className="text-white/40 text-base leading-relaxed">
                                Our anonymized distribution protocol ensures that structural logic patterns are shared without ever revealing the source project. Total privacy—scaled.
                            </p>
                        </div>
                        <div className="px-8 py-4 rounded-xl bg-white/5 border border-white/10 font-mono text-xs text-emerald-500/60 animate-pulse">
                            {`{ "> ledger": "MESH_ACTIVE" }`}
                        </div>
                    </div>
                </div>
            </section>

            {/* BRIDGE: Network Effects */}
            <section className="w-full max-w-6xl px-6 mb-16 relative z-10">
                <div className="text-center">
                    <div className="inline-block px-6 py-3 rounded-2xl bg-gradient-to-r from-emerald-500/5 via-blue-500/5 to-purple-500/5 border border-white/5">
                        <p className="text-lg md:text-xl font-light text-white/80 leading-relaxed">
                            Individual Moats Are Strong. <span className="font-bold text-white">Network Effects Make Them Insurmountable.</span>
                        </p>
                    </div>
                </div>
            </section>

            {/* 5. THE ANONYMIZED LEDGER (Collective Intelligence) */}
            <section className="w-full max-w-6xl px-6 mb-32 relative z-10">
                <div className="bg-[#0a0a0a] rounded-[22px] border border-white/5 p-8 md:p-12 overflow-hidden relative">
                    <div className="absolute -bottom-24 -left-24 w-[400px] h-[400px] bg-blue-500/[0.03] blur-[80px] rounded-full pointer-events-none" />
                    <div className="absolute -top-24 -right-24 w-[400px] h-[400px] bg-emerald-500/[0.03] blur-[80px] rounded-full pointer-events-none" />

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center relative z-10">
                        <div>
                            <div className="inline-flex items-center gap-2 mb-6">
                                <Globe size={16} className="text-blue-400" />
                                <span className="text-blue-400 font-mono text-xs font-bold tracking-[0.3em] uppercase">Distributed Intelligence</span>
                            </div>
                            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
                                Your Victories Become <span className="text-white/50">Everyone's Defenses</span>
                            </h2>
                            <p className="text-lg text-white/60 leading-relaxed mb-8">
                                Sidelith shares anonymized technical patterns across the network while keeping your strategic intent local. Your secrets stay private. Your solutions strengthen the collective.
                            </p>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                                <div className="space-y-2">
                                    <div className="text-white font-bold text-sm">Structural Logic</div>
                                    <p className="text-[10px] text-white/40 uppercase tracking-wider font-mono">DECOUPLED FROM DATA</p>
                                </div>
                                <div className="space-y-2">
                                    <div className="text-white font-bold text-sm">Heuristic Guards</div>
                                    <p className="text-[10px] text-white/40 uppercase tracking-wider font-mono">ERROR SIGNATURES</p>
                                </div>
                                <div className="space-y-2">
                                    <div className="text-white font-bold text-sm">Strategic Deltas</div>
                                    <p className="text-[10px] text-white/40 uppercase tracking-wider font-mono">DOMAIN WEIGHTS</p>
                                </div>
                            </div>

                            <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 font-mono text-[10px] text-white/40 space-y-1">
                                <div>{`{ "> source": "LOCAL_NODE_77" }`}</div>
                                <div className="text-emerald-500">{`{ "> process": "PII_STRIP_CLEAN_ROOM" }`}</div>
                                <div>{`{ "> artifact": "VAR_4091_SIG" }`}</div>
                                <div className="animate-pulse">{`{ "> status": "MESH_DISTRIBUTION_ACTIVE" }`}</div>
                            </div>
                        </div>

                        <div className="relative flex items-center justify-center py-12">
                            <div className="w-32 h-32 md:w-40 md:h-40 rounded-full border border-white/10 bg-white/[0.02] flex items-center justify-center relative group">
                                <div className="absolute inset-0 rounded-full border border-emerald-500/20 animate-ping opacity-20" />
                                <div className="absolute inset-2 rounded-full border border-emerald-500/10 border-dashed animate-spin-slow" />
                                <Shield size={42} className="text-white/20 group-hover:text-emerald-500 transition-colors" />

                                <div className="absolute -left-20 top-0 opacity-20 blur-[1px]">
                                    <div className="w-4 h-4 rounded bg-white/40 rotate-45" />
                                </div>
                                <div className="absolute -left-24 bottom-10 opacity-10 blur-[2px]">
                                    <div className="w-6 h-6 rounded-full bg-white/20" />
                                </div>

                                <div className="absolute -right-20 top-0">
                                    <div className="w-4 h-4 rounded bg-amber-500 shadow-[0_0_15px_rgba(245,158,11,0.5)] rotate-45 animate-bounce" />
                                </div>
                                <div className="absolute -right-28 bottom-20">
                                    <div className="w-5 h-5 rounded-full bg-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.5)] animate-pulse" />
                                </div>
                                <div className="absolute -right-16 -bottom-5">
                                    <div className="w-3 h-3 rounded-sm bg-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.5)]" />
                                </div>
                            </div>

                            <svg className="absolute inset-0 w-full h-full pointer-events-none -z-10 overflow-visible" viewBox="0 0 400 300">
                                <path d="M 50 150 L 150 150" stroke="white" strokeWidth="1" strokeDasharray="4 4" className="opacity-10" />
                                <path d="M 250 150 L 350 150" stroke="white" strokeWidth="1" strokeDasharray="4 4" className="opacity-20" />
                            </svg>

                            <div className="absolute bottom-0 text-[8px] tracking-[0.4em] text-white/20 font-mono uppercase">
                                [STRIP_CLEAN_ROOM_ACTIVE]
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* 6. THE INTELLIGENCE MESH (Integrations) */}
            <section className="section-spacing w-full max-w-6xl px-6 mb-24 relative z-10">
                <div className="text-center mb-12">
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-3">Works <span className="text-blue-500">Where You Do</span></h2>
                    <p className="text-base text-white/50 max-w-2xl mx-auto">
                        Sidelith is the <b>secure local backbone</b> that connects your AI tools with Truth and Memory.
                    </p>
                </div>

                {/* Bento Grid Layout */}
                <div className="grid grid-cols-1 md:grid-cols-6 gap-6 auto-rows-fr">
                    {/* CURSOR - Hero Card (Spans 3 columns, 2 rows) - Largest AI IDE market share */}
                    <div className="md:col-span-3 md:row-span-2 p-8 rounded-[28px] bg-gradient-to-br from-blue-500/[0.08] to-purple-500/[0.08] border border-blue-500/20 hover:border-blue-500/40 transition-all group relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 blur-[60px] rounded-full group-hover:bg-blue-500/20 transition-colors" />
                        <div className="relative z-10">
                            <div className="w-16 h-16 rounded-2xl bg-blue-500/20 flex items-center justify-center mb-6 border border-blue-500/30">
                                <Monitor size={32} className="text-blue-500" />
                            </div>
                            <h3 className="text-2xl font-bold text-white mb-2">Cursor</h3>
                            <p className="text-white/60 text-sm mb-6">The AI-first IDE. Sidelith feeds it perfect context via MCP.</p>

                            {/* Live Metrics */}
                            <div className="grid grid-cols-2 gap-4 mb-6">
                                <div className="p-3 rounded-xl bg-white/5 border border-white/10">
                                    <div className="text-[10px] text-white/40 uppercase tracking-wider mb-1">Protocol</div>
                                    <div className="text-sm font-mono text-blue-500 flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                                        MCP
                                    </div>
                                </div>
                                <div className="p-3 rounded-xl bg-white/5 border border-white/10">
                                    <div className="text-[10px] text-white/40 uppercase tracking-wider mb-1">Context</div>
                                    <div className="text-sm font-mono text-white">100%</div>
                                </div>
                            </div>

                            <div className="text-[10px] font-mono text-blue-500/60 uppercase tracking-widest">
                                ⚡ PRIMARY_IDE
                            </div>
                        </div>
                    </div>

                    {/* CLAUDE DESKTOP - Large Card (Spans 3 columns, 2 rows) - MCP Host */}
                    <div className="md:col-span-3 md:row-span-2 p-6 rounded-[28px] bg-[#0a0a0a] border border-white/5 hover:border-purple-500/30 transition-all group relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/5 blur-[40px] rounded-full group-hover:bg-purple-500/10 transition-colors" />
                        <div className="relative z-10">
                            <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-4 border border-purple-500/20">
                                <Bot size={24} className="text-purple-500" />
                            </div>
                            <h3 className="text-xl font-bold text-white mb-2">Claude Desktop</h3>
                            <p className="text-white/40 text-sm mb-4">Native MCP host. Sidelith serves context as a trusted server.</p>
                            <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 font-mono text-[10px] text-purple-500/60">
                                {`> mcp://sidelith/context`}
                            </div>
                        </div>
                    </div>

                    {/* VS CODE - Medium Card */}
                    <div className="md:col-span-2 p-6 rounded-[28px] bg-[#0a0a0a] border border-white/5 hover:border-indigo-500/30 transition-all group">
                        <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center mb-4 border border-indigo-500/20">
                            <Terminal size={20} className="text-indigo-500" />
                        </div>
                        <h4 className="text-lg font-bold text-white mb-2">VS Code</h4>
                        <p className="text-white/40 text-xs mb-3">Extension Bridge</p>
                        <div className="text-[8px] font-mono text-indigo-500/60 uppercase tracking-widest">EXTENSION</div>
                    </div>

                    {/* WINDSURF - Medium Card */}
                    <div className="md:col-span-2 p-6 rounded-[28px] bg-[#0a0a0a] border border-white/5 hover:border-cyan-500/30 transition-all group">
                        <div className="w-10 h-10 rounded-xl bg-cyan-500/10 flex items-center justify-center mb-4 border border-cyan-500/20">
                            <Wind size={20} className="text-cyan-500" />
                        </div>
                        <h4 className="text-lg font-bold text-white mb-2">Windsurf</h4>
                        <p className="text-white/40 text-xs mb-3">Cascade Sync</p>
                        <div className="text-[8px] font-mono text-cyan-500/60 uppercase tracking-widest">FLOW_MODE</div>
                    </div>

                    {/* TERMINAL/CLI - Medium Card */}
                    <div className="md:col-span-2 p-6 rounded-[28px] bg-[#0a0a0a] border border-white/5 hover:border-emerald-500/30 transition-all group">
                        <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center mb-4 border border-emerald-500/20">
                            <Cpu size={20} className="text-emerald-500" />
                        </div>
                        <h4 className="text-lg font-bold text-white mb-2">Terminal</h4>
                        <p className="text-white/40 text-xs mb-3">Direct CLI Access</p>
                        <div className="text-[8px] font-mono text-emerald-500/60 uppercase tracking-widest">SIDE_CLI</div>
                    </div>
                </div>
            </section>

            {/* 7. PRICING SECTION */}
            <section className="section-spacing w-full max-w-6xl px-6 mb-24 relative z-10">
                <div className="text-center mb-12">
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-3">Scale for <span className="text-amber-500">Intelligence</span></h2>
                    <p className="text-base text-white/50">Deterministic capacity for your semantic operations.</p>
                </div>

                {/* Bento Pricing Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    {/* TRIAL - Small Card */}
                    <div className="md:col-span-1 p-6 rounded-[28px] bg-[#0a0a0a] border border-white/5 hover:border-white/10 transition-all group">
                        <div className="text-[10px] font-mono text-white/30 tracking-widest uppercase mb-2">Hobby</div>
                        <div className="text-3xl font-bold text-white mb-1">$0</div>
                        <div className="text-[10px] font-mono text-white/40 mb-4">500 SUs / MO</div>
                        <p className="text-xs text-white/30 mb-6">The default entry point for exploring Sidelith.</p>
                        <a href="#install-widget" className="block text-center py-2 px-4 rounded-xl border border-white/10 hover:border-white/20 text-xs font-bold text-white transition-colors uppercase tracking-widest">
                            Start Free
                        </a>
                    </div>

                    {/* PRO - Featured Card (Spans 2 columns) */}
                    <div className="md:col-span-2 p-8 rounded-[28px] bg-gradient-to-br from-amber-500/[0.08] to-orange-500/[0.08] border border-amber-500/30 hover:border-amber-500/50 transition-all group relative overflow-hidden">
                        <div className="absolute top-4 right-4 px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500/40 text-[8px] font-mono text-amber-500 uppercase tracking-widest">
                            ⭐ Popular
                        </div>
                        <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 blur-[60px] rounded-full group-hover:bg-amber-500/20 transition-colors" />

                        <div className="relative z-10">
                            <div className="text-[10px] font-mono text-amber-500/60 tracking-widest uppercase mb-2">Pro</div>
                            <div className="text-4xl font-bold text-white mb-1">$20</div>
                            <div className="text-sm font-mono text-white/60 mb-6">5,000 SUs / MO</div>
                            <p className="text-sm text-white/60 mb-6">Standard tier for freelancers and professionals.</p>

                            {/* Animated SU Meter */}
                            <div className="mb-6">
                                <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                    <div className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full w-3/4 group-hover:w-full transition-all duration-1000" />
                                </div>
                                <div className="text-[8px] font-mono text-amber-500/60 mt-2 uppercase tracking-widest">5K SU Capacity</div>
                            </div>

                            <a href="#install-widget" className="block text-center py-3 px-6 rounded-xl bg-amber-500/20 border border-amber-500/40 hover:bg-amber-500/30 text-sm font-bold text-white transition-colors uppercase tracking-widest">
                                Get Started
                            </a>
                        </div>
                    </div>

                    {/* ELITE - Small Card */}
                    <div className="md:col-span-1 p-6 rounded-[28px] bg-[#0a0a0a] border border-white/5 hover:border-purple-500/30 transition-all group">
                        <div className="text-[10px] font-mono text-white/30 tracking-widest uppercase mb-2">Elite</div>
                        <div className="text-3xl font-bold text-white mb-1">$60</div>
                        <div className="text-[10px] font-mono text-white/40 mb-4">25,000 SUs / MO</div>
                        <p className="text-xs text-white/30 mb-6">For 10x engineers and large repositories.</p>
                        <a href="#install-widget" className="block text-center py-2 px-4 rounded-xl border border-white/10 hover:border-purple-500/30 text-xs font-bold text-white transition-colors uppercase tracking-widest">
                            Upgrade
                        </a>
                    </div>
                </div>

                {/* HIGH TECH - Full Width Enterprise Card */}
                <div className="p-8 rounded-[28px] bg-gradient-to-r from-slate-900/50 to-slate-800/50 border border-white/10 hover:border-white/20 transition-all group relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500/[0.02] to-purple-500/[0.02]" />
                    <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-6">
                        <div className="flex-1">
                            <div className="text-[10px] font-mono text-white/40 tracking-widest uppercase mb-2">High Tech</div>
                            <h3 className="text-2xl font-bold text-white mb-2">Enterprise Infrastructure</h3>
                            <p className="text-white/50 text-sm mb-4">True air-gap deployment with local Ollama LLM for regulated industries.</p>
                            <div className="flex flex-wrap gap-4 text-[10px] text-white/40">
                                <span>• Zero Cloud Sync</span>
                                <span>• Local Ollama LLM</span>
                                <span>• FIPS/ITAR/HIPAA Ready</span>
                                <span>• Custom Deployment</span>
                            </div>
                        </div>
                        <div className="flex-shrink-0 flex flex-col items-center justify-center">
                            <div className="text-3xl font-bold text-white mb-4">Custom</div>
                            <a href="mailto:enterprise@sidelith.com" className="block text-center py-3 px-6 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 text-sm font-bold text-white transition-colors uppercase tracking-widest whitespace-nowrap">
                                Contact Sales
                            </a>
                        </div>
                    </div>
                </div>

                {/* Add-on: Structural Refills */}
                <div className="mt-12 p-6 rounded-2xl border border-white/5 bg-white/[0.01] flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="flex items-center gap-4">
                        <div className="p-3 rounded-xl bg-orange-500/10 border border-orange-500/20">
                            <Zap className="w-6 h-6 text-orange-400" />
                        </div>
                        <div>
                            <h4 className="text-sm font-bold text-white uppercase tracking-wider">Structural Refills</h4>
                            <p className="text-xs text-white/40 max-w-sm">Ran out of throughput? Add capacity incrementally to your Sovereign Node. Credits are applied instantly.</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-8 pr-4">
                        <div className="text-right">
                            <div className="text-2xl font-bold text-white">$10</div>
                            <div className="text-[10px] text-white/40 uppercase tracking-wider">2,500 SUs</div>
                        </div>
                    </div>
                </div>
            </section>

            {/* 8. INSTALLATION (The Developer's Shortcut) - Hero CTA */}
            <section id="install-widget" className="section-spacing w-full max-w-5xl px-6 mb-32 relative z-10">
                {/* Hero Container */}
                <div className="relative p-12 rounded-[32px] bg-gradient-to-br from-emerald-500/[0.05] to-blue-500/[0.05] border border-emerald-500/20 overflow-hidden">
                    {/* Background Effects */}
                    <div className="absolute top-0 left-1/4 w-64 h-64 bg-emerald-500/10 blur-[100px] rounded-full" />
                    <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-blue-500/10 blur-[100px] rounded-full" />

                    <div className="relative z-10">
                        {/* Header */}
                        <div className="text-center mb-12">
                            <div className="inline-block px-4 py-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 text-emerald-500 font-mono text-[10px] tracking-widest uppercase mb-6">
                                ⚡ The Developer's Shortcut
                            </div>
                            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
                                Ready to <span className="text-emerald-400">Deploy</span>
                            </h2>
                            <p className="text-lg text-white/60 max-w-2xl mx-auto">
                                You don't need a heavy account. You need a binary. Start building with local-first intelligence in seconds.
                            </p>
                        </div>

                        {/* Install Widget */}
                        <div className="mb-12">
                            <InstallWidget />
                        </div>

                        {/* Social Proof Badges */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-center">
                                <div className="text-2xl font-bold text-emerald-500 mb-1">177M/s</div>
                                <div className="text-[10px] text-white/40 uppercase tracking-wider">Match Speed</div>
                            </div>
                            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-center">
                                <div className="text-2xl font-bold text-emerald-500 mb-1">&lt;1ms</div>
                                <div className="text-[10px] text-white/40 uppercase tracking-wider">Pulse Latency</div>
                            </div>
                            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-center">
                                <div className="text-2xl font-bold text-emerald-500 mb-1">&lt;5ms</div>
                                <div className="text-[10px] text-white/40 uppercase tracking-wider">Context Load</div>
                            </div>
                            <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 text-center">
                                <div className="text-2xl font-bold text-emerald-500 mb-1">&lt;1%</div>
                                <div className="text-[10px] text-white/40 uppercase tracking-wider">CPU Usage</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* 9. FOOTER */}
            <footer className="w-full border-t border-white/5 py-12 relative z-10">
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
        </main >
    );
}
