import { Terminal, Shield, Zap, Cpu, Database, Globe, Sparkles, Lock } from "lucide-react";

export function SolutionSolarSystem() {
    return (
        <section className="section-spacing w-full max-w-6xl px-4 z-10 relative">
            <div className="text-center mb-32">
                <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                    The <span className="text-neon">System Shield</span>.
                </h2>
                <p className="text-xl text-white/40 font-light max-w-2xl mx-auto">
                    A deterministic loop that replaces noise with truth.
                </p>
            </div>

            {/* THE SYSTEM SOLAR SYSTEM (HEXAGON ORBIT) */}
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
                    <p className="text-xs text-white/50 max-w-[150px]">The System Gate.</p>
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
                        { id: "05", label: "LEARNING", icon: Terminal, color: "text-white", border: "border-white/40", shadow: "shadow-white/10", sub: "Save \u0026 Evolve" }
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
                    {`\u003e origin: "User Request"`} <br />
                    {`\u003e velocity: 120ms`} <br />
                    {`\u003e status: VECTOR_CAPTURED`} <br />
                    {`\u003e scan: 177,402 ops/s`} <br />
                    <span className="text-emerald-400">{`\u003e merkle_tree: UPDATED`}</span>
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
                    {`\u003e\u003e POLICY_CHECK: PASS`} <br />
                    {`\u003e\u003e ISOLATION: 100%`}
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
                    <h3 className="text-2xl font-bold text-white mb-4">03. Structural Integrity.</h3>
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
                    <h3 className="text-2xl font-bold text-white mb-4">05. Episodic Memory.</h3>
                    <p className="text-white/40 text-lg font-light leading-relaxed">
                        Verified solutions are serialized into the Chronos Vector Store. Sidelith captures the Reasoning Graph, Verified Patterns, and Forensic Guards from this interaction, ensuring the Operator never repeats a mistake.
                    </p>
                    <div className="mt-6 p-4 rounded-xl bg-amber-500/[0.03] border border-amber-500/10 font-mono text-[10px] text-amber-500/60 transition-all hover:bg-amber-500/[0.06]">
                        {`\u003e update: NEURAL_LOGIC_GRAPH`} <br />
                        {`\u003e serialized: [REASONING_GRAPH, PATTERN_V4]`} <br />
                        <span className="text-amber-500 font-bold">{`\u003e status: KNOWLEDGE_BASE_UPDATED`}</span>
                    </div>
                </div>
            </div>
        </section>
    );
}
