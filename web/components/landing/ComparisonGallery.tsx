"use client";

import { Check, X, Terminal, FileCode, AlertCircle, Database, Settings, Server } from "lucide-react";
import { useState } from "react";

type Scenario = "routes" | "data" | "config";
type Mode = "without" | "with";

export function ComparisonGallery() {
    const [activeScenario, setActiveScenario] = useState<Scenario>("routes");
    const [activeMode, setActiveMode] = useState<Mode>("without");

    const scenarios = {
        routes: {
            icon: Server,
            label: "API Routes",
            file: activeMode === "with" ? "src/routes/payment.ts" : "app.js",
            code: activeMode === "without" ? (
                // WITHOUT SIDELITH (BAD CODE)
                <div className="space-y-1 animate-in fade-in duration-300">
                    <div className="text-zinc-500">// ❌ WRONG FILE: Placed in root instead of /src/routes</div>
                    <div className="text-zinc-500">// ❌ OLD PATTERN: Uses callbacks instead of async/await</div>
                    <div className="text-zinc-500">// ❌ LEGACY: No validation middleware</div>
                    <br />
                    <div><span className="text-purple-400">const</span> app = <span className="text-blue-400">express</span>();</div>
                    <br />
                    <div>app.<span className="text-blue-400">post</span>(<span className="text-orange-300">"/pay"</span>, (req, res) ={">"} {"{"}</div>
                    <div className="pl-4">
                        <span className="text-blue-400">processPayment</span>(req.body, (err, result) ={">"} {"{"}</div>
                    <div className="pl-8">
                        <span className="text-purple-400">if</span> (err) <span className="text-purple-400">return</span> res.<span className="text-blue-400">send</span>(500);
                    </div>
                    <div className="pl-8">
                        res.<span className="text-blue-400">json</span>({"{"} success: <span className="text-orange-300">true</span> {"}"});
                    </div>
                    <div className="pl-4">{"}"});</div>
                    <div>{"}"});</div>
                </div>
            ) : (
                // WITH SIDELITH (GOOD CODE)
                <div className="space-y-1 animate-in fade-in duration-300">
                    <div className="text-zinc-500">// ✅ CORRECT FILE: Detected Pattern: Modular Routes</div>
                    <div className="text-zinc-500">// ✅ MODERN SYNTAX: Detected Pattern: Async/Await</div>
                    <div className="text-zinc-500">// ✅ INPUT SAFETY: Enforced Zod Schema</div>
                    <br />
                    <div><span className="text-purple-400">import</span> {"{"} PaymentSchema {"}"} <span className="text-purple-400">from</span> <span className="text-orange-300">"../schemas"</span>;</div>
                    <br />
                    <div>router.<span className="text-blue-400">post</span>(<span className="text-orange-300">"/"</span>, <span className="text-purple-400">async</span> (req, res, next) ={">"} {"{"}</div>
                    <div className="pl-4"><span className="text-purple-400">try</span> {"{"}</div>
                    <div className="pl-8"><span className="text-purple-400">const</span> payload = PaymentSchema.<span className="text-blue-400">parse</span>(req.body);</div>
                    <div className="pl-8"><span className="text-purple-400">const</span> result = <span className="text-purple-400">await</span> Service.<span className="text-blue-400">charge</span>(payload);</div>
                    <div className="pl-8">res.<span className="text-blue-400">json</span>(result);</div>
                    <div className="pl-4">{"}"} <span className="text-purple-400">catch</span> (e) {"{"} <span className="text-blue-400">next</span>(e); {"}"}</div>
                    <div>{"}"});</div>
                </div>
            ),
            analysis: activeMode === "without" ? [
                { icon: X, color: "text-red-500", title: "Context Hallucination", desc: "AI guesses project structure based on generic internet training data." },
                { icon: AlertCircle, color: "text-orange-500", title: "Pattern Drift", desc: "Introduces legacy callbacks into a modern async/await codebase." }
            ] : [
                { icon: Check, color: "text-emerald-400", title: "Architectural Alignment", desc: "Sidelith injected src/routes/** pattern into the context window." },
                { icon: Check, color: "text-emerald-400", title: "Type Safety Enforced", desc: "Detected zod usage in other files and forced the AI to prompt for schemas." }
            ]
        },
        data: {
            icon: Database,
            label: "Database Actions",
            file: activeMode === "with" ? "src/db/queries.ts" : "users.js",
            code: activeMode === "without" ? (
                // WITHOUT SIDELITH (BAD CODE)
                <div className="space-y-1 animate-in fade-in duration-300">
                    <div className="text-zinc-500">// ❌ SECURITY RISK: String interpolation</div>
                    <div className="text-zinc-500">// ❌ FRAGILE: Hardcoded table names</div>
                    <br />
                    <div><span className="text-purple-400">const</span> query = <span className="text-orange-300">`SELECT * FROM users WHERE id = <span className="text-white">${"{"}req.params.id{"}"}</span>`</span>;</div>
                    <br />
                    <div>db.<span className="text-blue-400">execute</span>(query, (err, rows) ={">"} {"{"}</div>
                    <div className="pl-4"><span className="text-purple-400">if</span> (err) <span className="text-blue-400">console</span>.<span className="text-blue-400">error</span>(err);</div>
                    <div className="pl-4"><span className="text-purple-400">return</span> rows[0];</div>
                    <div>{"}"});</div>
                </div>
            ) : (
                // WITH SIDELITH (GOOD CODE)
                <div className="space-y-1 animate-in fade-in duration-300">
                    <div className="text-zinc-500">// ✅ SAFE: Parameterized Query Builder</div>
                    <div className="text-zinc-500">// ✅ TYPED: Infers constraints from Schema</div>
                    <br />
                    <div><span className="text-purple-400">import</span> {"{"} db {"}"} <span className="text-purple-400">from</span> <span className="text-orange-300">"../lib/db"</span>;</div>
                    <br />
                    <div><span className="text-purple-400">const</span> user = <span className="text-purple-400">await</span> db</div>
                    <div className="pl-4">.<span className="text-blue-400">selectFrom</span>(<span className="text-orange-300">"users"</span>)</div>
                    <div className="pl-4">.<span className="text-blue-400">where</span>(<span className="text-orange-300">"id"</span>, <span className="text-orange-300">"="</span>, id)</div>
                    <div className="pl-4">.<span className="text-blue-400">executeTakeFirst</span>();</div>
                    <br />
                    <div><span className="text-purple-400">if</span> (!user) <span className="text-purple-400">throw</span> <span className="text-purple-400">new</span> <span className="text-blue-400">NotFoundError</span>();</div>
                </div>
            ),
            analysis: activeMode === "without" ? [
                { icon: X, color: "text-red-500", title: "SQL Injection Vector", desc: "Suggests dangerous string interpolation." },
                { icon: AlertCircle, color: "text-orange-500", title: "Untyped Response", desc: "Returns 'any', breaking TypeScript strictness." }
            ] : [
                { icon: Check, color: "text-emerald-400", title: "Schema Awareness", desc: "Read schema.prisma to suggest typesafe query builder methods." },
                { icon: Check, color: "text-emerald-400", title: "Error Handling", desc: "Added explicit check for missing record." }
            ]
        },
        config: {
            icon: Settings,
            label: "Configuration",
            file: activeMode === "with" ? "src/config/env.ts" : "server.js",
            code: activeMode === "without" ? (
                // WITHOUT SIDELITH (BAD CODE)
                <div className="space-y-1 animate-in fade-in duration-300">
                    <div className="text-zinc-500">// ❌ SILENT FAILURE: No validation on startup</div>
                    <div className="text-zinc-500">// ❌ HARDCODED: Defaults scattered in code</div>
                    <br />
                    <div><span className="text-purple-400">const</span> port = process.env.PORT || 3000;</div>
                    <div><span className="text-purple-400">const</span> dbUrl = process.env.DATABASE_URL;</div>
                    <br />
                    <div>mongoose.<span className="text-blue-400">connect</span>(dbUrl); <span className="text-zinc-500">// crashes later if undef</span></div>
                </div>
            ) : (
                // WITH SIDELITH (GOOD CODE)
                <div className="space-y-1 animate-in fade-in duration-300">
                    <div className="text-zinc-500">// ✅ CENTRALIZED: Single source of truth</div>
                    <div className="text-zinc-500">// ✅ VALIDATED: Fails fast on startup</div>
                    <br />
                    <div><span className="text-purple-400">import</span> {"{"} z {"}"} <span className="text-purple-400">from</span> <span className="text-orange-300">"zod"</span>;</div>
                    <br />
                    <div><span className="text-purple-400">export const</span> env = z.<span className="text-blue-400">object</span>({"{"}</div>
                    <div className="pl-4">PORT: z.coerce.<span className="text-blue-400">number</span>().<span className="text-blue-400">default</span>(3000),</div>
                    <div className="pl-4">DATABASE_URL: z.<span className="text-blue-400">string</span>().<span className="text-blue-400">url</span>(),</div>
                    <div>{"}"}).<span className="text-blue-400">parse</span>(process.env);</div>
                </div>
            ),
            analysis: activeMode === "without" ? [
                { icon: X, color: "text-red-500", title: "Runtime Fragility", desc: "App might start but fail hours later when accessing a missing env var." },
                { icon: AlertCircle, color: "text-orange-500", title: "Type Loose", desc: "Treats all env vars as strings or undefined." }
            ] : [
                { icon: Check, color: "text-emerald-400", title: "Startup Safety", desc: "Enforced Zod validation pattern detected in project." },
                { icon: Check, color: "text-emerald-400", title: "Type Inference", desc: "Exports fully typed configuration object." }
            ]
        }
    };

    const currentScenario = scenarios[activeScenario];

    return (
        <section className="w-full max-w-6xl mx-auto py-16 px-6">
            <div className="text-center mb-16">
                <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                    Context is <span className={activeMode === "with" ? "text-emerald-400" : "text-red-500"}>Everything</span>.
                </h2>
                <p className="text-white/50 text-lg max-w-2xl mx-auto">
                    Without Sidelith, AI guesses. With Sidelith, AI knows.
                </p>
            </div>

            {/* Scenario Tabs (Palantir Style) */}
            <div className="flex justify-center mb-12">
                <div className="flex bg-white/5 rounded-lg p-1 border border-white/10">
                    {(Object.keys(scenarios) as Scenario[]).map((s) => {
                        const Icon = scenarios[s].icon;
                        const isActive = activeScenario === s;
                        return (
                            <button
                                key={s}
                                onClick={() => setActiveScenario(s)}
                                className={`flex items-center gap-2 px-6 py-2 rounded-md text-sm font-mono font-bold transition-all ${isActive
                                    ? "bg-white text-black shadow-lg"
                                    : "text-white/40 hover:text-white hover:bg-white/5"
                                    }`}
                            >
                                <Icon size={14} />
                                {scenarios[s].label}
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Main Window */}
            <div className={`rounded-3xl border transition-all duration-500 overflow-hidden relative group min-h-[500px] flex flex-col ${activeMode === "with"
                ? "border-emerald-500/30 bg-[#0a0f0d] shadow-[0_0_100px_rgba(16,185,129,0.1)]"
                : "border-red-500/30 bg-[#0f0a0a] shadow-[0_0_100px_rgba(239,68,68,0.1)]"
                }`}>

                {/* Window Controls & Toggle */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-white/[0.02]">
                    <div className="flex items-center gap-4">
                        <div className="flex gap-2">
                            <div className="w-3 h-3 rounded-full bg-red-500/50" />
                            <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
                            <div className="w-3 h-3 rounded-full bg-green-500/50" />
                        </div>
                        <div className="flex items-center gap-2 text-xs font-mono text-white/30 ml-4 border-l border-white/10 pl-4">
                            <FileCode size={12} />
                            {currentScenario.file}
                        </div>
                    </div>

                    {/* Mode Toggle inside the window header */}
                    <div className="flex items-center bg-black/50 rounded-lg p-1 border border-white/5">
                        <button
                            onClick={() => setActiveMode("without")}
                            className={`px-3 py-1 rounded-md text-[10px] uppercase font-bold tracking-wider transition-all ${activeMode === "without" ? "bg-red-500/20 text-red-500" : "text-white/20 hover:text-white/50"
                                }`}
                        >
                            Without
                        </button>
                        <div className="w-px h-3 bg-white/10 mx-1"></div>
                        <button
                            onClick={() => setActiveMode("with")}
                            className={`px-3 py-1 rounded-md text-[10px] uppercase font-bold tracking-wider transition-all ${activeMode === "with" ? "bg-emerald-500/20 text-emerald-400" : "text-white/20 hover:text-white/50"
                                }`}
                        >
                            With Sidelith
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 flex-grow">

                    {/* Code Editor */}
                    <div className="p-8 font-mono text-sm overflow-x-auto relative">
                        {currentScenario.code}

                        {/* Background Noise */}
                        <div className="absolute top-0 right-0 w-full h-full pointer-events-none opacity-20 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] mix-blend-overlay"></div>
                    </div>

                    {/* Analysis Sidebar */}
                    <div className={`p-8 border-l backdrop-blur-sm transition-colors duration-500 flex flex-col justify-center ${activeMode === "with"
                        ? "border-emerald-500/10 bg-emerald-500/[0.02]"
                        : "border-red-500/10 bg-red-500/[0.02]"
                        }`}>
                        <div className="flex items-center gap-2 mb-8 text-xs font-mono uppercase tracking-widest opacity-50">
                            <Terminal size={14} />
                            AI Reasoning Log
                        </div>

                        <div className="space-y-8">
                            {currentScenario.analysis.map((item, i) => (
                                <div key={i} className="flex gap-4 animate-in slide-in-from-right-4 duration-500" style={{ animationDelay: `${i * 100}ms` }}>
                                    <div className={`shrink-0 mt-1 ${item.color}`}>
                                        <item.icon size={20} />
                                    </div>
                                    <div>
                                        <h4 className={`font-bold text-sm mb-1 ${item.color}`}>{item.title}</h4>
                                        <p className={`text-xs leading-relaxed opacity-70 ${activeMode === "with" ? "text-emerald-100" : "text-red-100"
                                            }`}>
                                            {item.desc}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
