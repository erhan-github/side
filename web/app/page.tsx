"use client";

import { Terminal, ChevronRight, Zap, Copy, Brain, Shield, Users, Eye, FileText, Check, X, AlertCircle, GitBranch, RefreshCw, AlertTriangle, ChevronDown, Globe, Lock } from "lucide-react";
import Link from "next/link";
import { useState, useEffect } from "react";
import { RotatingRole } from "@/components/ui/RotatingRole";

// Real C-Level roles mapped to ACTUAL features


// ----------------------------------------------------------------------
// Palantir-Level Technical Specs
// ----------------------------------------------------------------------
type CapabilitySpec = {
  description: string;
  specs: { label: string; value: string }[];
  moat: string;
};

const CAPABILITY_SPECS: Record<string, CapabilitySpec> = {
  "Neural Logic Graph": {
    description: "Sidelith constructs a high-fidelity Knowledge Graph of your codebase's invisible logic threads with zero-latency local sync.",
    specs: [
      { label: "Engine", value: "Multi-Pass Tree-Sitter" },
      { label: "Topology", value: "Directed Semantic Graph" },
      { label: "Precision", value: "Function-Level" }
    ],
    moat: "• Pre-baked logic caches\n• Maps imports & side-effects\n• Infinite depth recursive search"
  },
  "The Strategic Registry": {
    description: "The definitive 'System of Record' (SoR) for project trajectory. 100% GDPR-sanitized cloud sync with local persistence.",
    specs: [
      { label: "Sync", value: "Judicial Scrubbing (Cloud)" },
      { label: "Storage", value: "Local SQLite + Supabase" },
      { label: "License", value: "MIT (Open Standards)" }
    ],
    moat: "• Judicial PII Redaction\n• Immutable Audit Chain\n• Cross-IDE context hydration"
  },
  "Architectural Forensics": {
    description: "Real-time drift detection. Compare implementation against roadmap to flag technical debt using a 400-point IQ scale.",
    specs: [
      { label: "Scale", value: "400-Point Strategic IQ" },
      { label: "Dimensions", value: "10 (Security to Investor)" },
      { label: "Health", value: "Forensic + Strategic Pillar" }
    ],
    moat: "• Detects circular dependencies\n• Flags pattern divergence\n• Automated debt tracking"
  },
  "Context-Engine (RLM)": {
    description: "Eliminate 'Context Rot'. Sidelith targets <110ms TTFT performance for global-scale architectural queries.",
    specs: [
      { label: "TTFT", value: "< 110ms (Groq 70B)" },
      { label: "Cache", value: "Article Score Pruning" },
      { label: "Scale", value: "10M+ User Architecture" }
    ],
    moat: "• No 'Needle-in-Haystack' errors\n• Hierarchical context retrieval\n• Semantic truth vs Guessing"
  }
};

export default function Home() {
  const [activeCase, setActiveCase] = useState("auth");
  const [simulationActive, setSimulationActive] = useState(false);
  const [activeFeature, setActiveFeature] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText("pip install sidelith");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };



  return (
    <div className="min-h-screen bg-black text-white selection:bg-emerald-500/30 font-sans">
      {/* Search Engine Dominance: JSON-LD */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "Side",
            "operatingSystem": "Universal",
            "applicationCategory": "DeveloperApplication",
            "offers": {
              "@type": "Offer",
              "price": "0",
              "priceCurrency": "USD"
            },
            "description": "Deterministic System of Record for modern software engineering teams."
          })
        }}
      />
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-black/50 backdrop-blur-md">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="h-6 w-6 bg-white rounded-sm group-hover:rotate-90 transition-transform duration-500" />
            <span className="font-black tracking-tighter text-xl uppercase italic text-white underline decoration-white/20 underline-offset-4">Sidelith</span>
          </Link>
          <div className="flex items-center gap-6 text-sm font-medium text-zinc-300">
            <Link href="#forensics" className="hover:text-white transition-colors">Forensics</Link>
            <Link href="#trust" className="hover:text-white transition-colors">Trust Protocol</Link>
            <Link href="#install" className="hover:text-white transition-colors">Install</Link>
            <Link href="/pricing" className="hover:text-white transition-colors">Infrastructure</Link>
            <Link href="/login" className="flex items-center gap-2 text-white bg-white/10 px-5 py-2 rounded-full hover:bg-white/20 transition-all font-bold border border-white/5 uppercase tracking-widest">
              Authenticate <ChevronRight className="w-3 h-3" />
            </Link>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6">
        {/* Section 1: Hero - Sovereign Integrity */}
        <section className="min-h-[95vh] flex flex-col items-center justify-center text-center pb-48 pt-64">
          <h1 className="text-[var(--text-hero)] mb-12">
            Sovereign <br />Integrity.
          </h1>
          <p className="text-[var(--text-body)] text-zinc-500 uppercase tracking-[0.4em] font-black max-w-5xl leading-tight">
            Built on deterministic <span className="text-white">Truth</span>, not generative guesses.
          </p>

          <div className="mt-24 space-y-12 flex flex-col items-center">
            <button
              onClick={handleCopy}
              className="h-24 px-16 bg-white text-black font-black text-2xl uppercase italic tracking-tighter font-heading hover:bg-zinc-200 transition-all flex items-center gap-6"
            >
              <Terminal className="w-8 h-8" />
              <span>pip install sidelith</span>
              {copied && <Check className="w-6 h-6 text-emerald-truth animate-in fade-in" />}
            </button>

            <div className="flex gap-20 font-black uppercase tracking-[0.4em] text-zinc-800">
              <span className="flex items-center gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-truth" /> Registry Active
              </span>
              <span className="flex items-center gap-3">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-truth" /> IQ: 400st
              </span>
            </div>
          </div>
        </section>

        {/* Section 2: The Logic Guard (Deterministic Knowledge) */}
        <section id="logic" className="py-[30vh] border-t border-white/5">
          <div className="max-w-5xl mx-auto space-y-20">
            <header className="space-y-6">
              <h2 className="text-[var(--text-h2)]">
                The Logic <br />Guard.
              </h2>
              <p className="text-[var(--text-body)] text-zinc-400 font-medium italic border-l-4 border-emerald-truth pl-8 py-2">
                Sidelith monitors the <span className="text-white">Invisible Why</span>. When you close your IDE, your architectural intent is secured in the Registry.
              </p>
            </header>

            {/* Perfect Frame: Truth vs Guess */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-white/5 border border-white/10 overflow-hidden">
              <div className="p-16 bg-black space-y-8">
                <h3 className="text-xs font-black uppercase tracking-[0.4em] text-red-500/50 italic">Generative Guessing</h3>
                <p className="text-sm text-zinc-500 leading-relaxed max-w-sm">
                  "Maybe the user meant this auth pattern. I will attempt to halluncinate a context match."
                </p>
                <div className="h-1 w-full bg-red-900/20 rounded-full overflow-hidden">
                  <div className="h-full bg-red-800 w-[20%] animate-pulse" />
                </div>
              </div>

              <div className="p-16 bg-black space-y-8 border-l border-white/10">
                <h3 className="text-xs font-black uppercase tracking-[0.4em] text-emerald-truth italic">Sovereign Truth</h3>
                <p className="text-sm text-zinc-300 leading-relaxed max-w-sm font-medium">
                  "Registry match found. Logic thread Jan14 confirms JWT rationale. Auditing implementation against AST."
                </p>
                <div className="h-1 w-full bg-emerald-truth/20 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-truth w-full" />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Section 2.5: The Registry Ledger (MONOLITH.md Visual) */}
        <section className="py-[30vh] border-t border-white/5 bg-zinc-900/5">
          <div className="max-w-5xl mx-auto space-y-24">
            <div className="text-center space-y-6">
              <h2 className="text-[var(--text-h2)]">Deterministic <br />Architecture.</h2>
              <p className="text-zinc-500 text-[10px] font-black uppercase tracking-[0.5em]">Side maintains Ground-Truth in a local <code className="text-emerald-truth">MONOLITH.md</code>.</p>
            </div>

            <div className="border border-white/10 bg-black overflow-hidden flex flex-col h-[600px] shadow-2xl">
              <div className="h-12 bg-zinc-900/50 flex items-center justify-between px-6 border-b border-white/5">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-white/10" />
                  <div className="w-3 h-3 rounded-full bg-white/10" />
                  <div className="w-3 h-3 rounded-full bg-white/10" />
                </div>
                <div className="text-[10px] font-mono text-zinc-500">.side/MONOLITH.md — SYSTEM_LEDGER</div>
                <div className="text-[10px] font-mono text-emerald-truth">SEALED_NODE</div>
              </div>

              <div className="flex-1 flex font-mono text-xs">
                <div className="w-48 border-r border-white/5 bg-zinc-950 p-6 space-y-4 text-zinc-600">
                  <div className="font-black text-[10px] text-zinc-400">EXPLORER</div>
                  <div className="space-y-2">
                    <div className="text-white">SIREN-LEDGER</div>
                    <div className="pl-4">src</div>
                    <div className="pl-4">tests</div>
                    <div className="pl-4 text-emerald-truth">MONOLITH.md</div>
                  </div>
                </div>
                <div className="flex-1 p-12 overflow-y-auto space-y-12 leading-relaxed bg-black">
                  <div className="space-y-4">
                    <h4 className="text-emerald-truth font-black uppercase italic tracking-tighter text-xl">PRIME_REGISTRY // V4.2</h4>
                    <p className="text-zinc-500">"Logic thread auth_sync suffering from context fragmentation. Flatten logic chain now or risk hydration debt in Q3."</p>
                  </div>

                  {/* Tactical Simulation Trigger */}
                  <div
                    onClick={() => setSimulationActive(!simulationActive)}
                    className="p-8 border border-white/10 bg-zinc-900/40 space-y-6 cursor-pointer hover:border-emerald-truth transition-all group"
                  >
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] font-black uppercase tracking-[0.4em] text-zinc-600 group-hover:text-emerald-truth transition-colors">Siren Simulation</span>
                      {simulationActive ? (
                        <span className="text-[10px] font-mono text-emerald-truth animate-pulse">PROBE_COMPLETE</span>
                      ) : (
                        <span className="text-[10px] font-mono text-zinc-700">READY_FOR_PROBE</span>
                      )}
                    </div>
                    <div className="space-y-4">
                      <p className="text-xs text-zinc-400">"Hey Side, {simulationActive ? "audit trajectory drift on auth_node_9." : "initiate forensic probe."}"</p>
                      {simulationActive && (
                        <div className="bg-black p-4 border border-emerald-truth/20 font-mono text-[11px] text-emerald-truth animate-in fade-in slide-in-from-bottom-2">
                          TRACE_RESULT: Divergence found in ServerAction. Hydration-lock applied.
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-12 pt-12 border-t border-white/10">
                    <div className="space-y-4">
                      <div className="text-[10px] font-black uppercase tracking-widest text-zinc-600">01_VITAL_FORENSICS</div>
                      <div className="space-y-2">
                        <div className="flex justify-between"><span>Semantic Depth</span><span className="text-emerald-truth">94%</span></div>
                        <div className="flex justify-between"><span>Logic Velocity</span><span className="text-emerald-truth">STABLE</span></div>
                        <div className="flex justify-between text-red-500"><span>Context Drift</span><span>CRITICAL</span></div>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div className="text-[10px] font-black uppercase tracking-widest text-zinc-600">02_FORENSIC_THREADS</div>
                      <div className="space-y-2">
                        <div className="flex gap-3"><span>T1</span><span className="text-zinc-400">Optimization: rust_macros</span></div>
                        <div className="flex gap-3"><span>T2</span><span className="text-zinc-400">Scrub: payment_webhooks</span></div>
                        <div className="flex gap-3"><span>T3</span><span className="text-white italic">Fix: state_sync</span></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Section 2.7: Forensic Evidence (Interactive Case Logs) */}
        <section id="evidence" className="py-[30vh] border-t border-white/5">
          <div className="max-w-6xl mx-auto space-y-24">
            <header className="text-center space-y-6">
              <h2 className="text-[var(--text-h2)]">Forensic <br />Evidence.</h2>
              <p className="text-[var(--text-body)] text-zinc-500 uppercase tracking-[0.4em] font-black">When Side saves you from a 2-week mistake, it pays for itself forever.</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-24">
              {/* Massive Trigger Grid */}
              <div className="grid grid-cols-2 gap-6">
                {[
                  { id: "auth", label: "Isomorphic Drift", save: "Fixed Hydration" },
                  { id: "research", label: "Cost Forensics", save: "- $4.2k/mo" },
                  { id: "fork", label: "Recursive Macros", save: "AST Precise" },
                  { id: "sec", label: "Judicial Scrub", save: "PII Secured" }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveCase(tab.id)}
                    className={`p-8 text-left border transition-all flex flex-col justify-between h-48 ${activeCase === tab.id
                      ? "bg-white text-black border-white"
                      : "bg-black text-zinc-500 border-white/10 hover:border-white/30"
                      }`}
                  >
                    <span className="text-[10px] font-black uppercase tracking-widest">{tab.save}</span>
                    <span className="text-xl font-black uppercase italic leading-none">{tab.label}</span>
                  </button>
                ))}
              </div>

              {/* Result Panel */}
              <div className="border border-white/10 p-16 space-y-12 bg-zinc-900/20 relative">
                <header className="flex justify-between items-center text-[10px] font-black uppercase tracking-[0.4em] text-emerald-truth">
                  <span>Forensic Thread: T3_SYNC</span>
                  <span>100% Integrity</span>
                </header>

                <div className="space-y-8">
                  <p className="text-2xl font-black italic text-white leading-tight">
                    {activeCase === 'auth' && "Logic thread Jan14 flagged for hydration drift. Side detected SSR/HMR cache mismatch."}
                    {activeCase === 'research' && "LLM Cost Forecast: Reasoning threads on 70B yielding <30% accuracy. Recommend escalation."}
                    {activeCase === 'fork' && "Multi-pass analysis stalling at depth 4 in Rust macros. Recursive scan required."}
                    {activeCase === 'sec' && "Registry Scan: Found raw PII in webhook debug logs. Enable forensic masking?"}
                  </p>

                  <div className="font-mono text-xs text-zinc-500 border-l border-white/10 pl-8 space-y-4">
                    {activeCase === 'auth' && (
                      <>
                        <p>"Correction Applied: force-dynamic enforced. Trajectory drift neutralized."</p>
                        <div className="text-emerald-truth font-black">SYSTEM IQ: +12 Points</div>
                      </>
                    )}
                    {activeCase === 'sec' && (
                      <>
                        <p>"Action: Judicial Masking applied to 12 PII nodes. Integrity preserved."</p>
                        <div className="text-emerald-truth font-black">REGISTRY: SEALED</div>
                      </>
                    )}
                    {(activeCase !== 'auth' && activeCase !== 'sec') && (
                      <p>"Registry maintaining 100% integrity across this strategic bridge."</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Section 2.9: The Sovereign Trust Protocol */}
        <section id="trust" className="py-[30vh] border-t border-white/5 bg-black">
          <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-24 items-center">
            <header className="space-y-12">
              <h2 className="text-[var(--text-h2)]">The Sovereign<br />Trust Protocol.</h2>
              <p className="text-[var(--text-body)] text-zinc-500">Side is built on deterministic truth. We don't ask for your trust; we prove it through architectural transparency.</p>
            </header>

            <div className="space-y-16">
              {[
                { title: "Zero-Keylogging", desc: "We monitor filesystem events, not keystrokes. Side only hears what you commit to disk." },
                { title: "Manual Trigger", desc: "No autonomous mutation. Every fix requires a deliberate user action and explicit approval." },
                { title: "Local Sovereignty", desc: "100% of code parsing happens on your machine. We sync metadata, never your source code." }
              ].map((item, i) => (
                <div key={i} className="space-y-4">
                  <h3 className="text-2xl font-black uppercase italic text-white">{item.title}</h3>
                  <p className="text-zinc-500 text-sm font-medium leading-relaxed">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Section 3: System of Record (The Immutable Ledger) */}
        <section id="record" className="py-[30vh] border-t border-white/5">
          <div className="max-w-5xl mx-auto space-y-20">
            <header className="space-y-6">
              <h2 className="text-[var(--text-h2)]">
                System of <br />Record.
              </h2>
              <p className="text-[var(--text-body)] text-zinc-400">
                Editors manage text. Agents manage action. Side manages <span className="text-white font-black underline decoration-white/20 underline-offset-8">Truth</span>.
              </p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
              <div className="p-12 border border-white/10 space-y-6">
                <h3 className="text-lg font-black uppercase italic">Immutable</h3>
                <p className="text-xs text-zinc-500 leading-relaxed">Trajectory secured in local Ledger nodes.</p>
                <div className="font-mono text-zinc-700">AES-256 [ENFORCED]</div>
              </div>
              <div className="p-12 border border-white/10 space-y-6">
                <h3 className="text-lg font-black uppercase italic">Deterministic</h3>
                <p className="text-xs text-zinc-500 leading-relaxed">Tree-Sitter AST parsing vs probabilistic guessing.</p>
                <div className="font-mono text-zinc-700">NODE_COUNT: 14M+</div>
              </div>
              <div className="p-12 border border-white/10 space-y-6">
                <h3 className="text-lg font-black uppercase italic">Forensic</h3>
                <p className="text-xs text-zinc-500 leading-relaxed">Real-time drift detection for project integrity.</p>
                <div className="font-mono text-zinc-700">INTEGRITY: 100%</div>
              </div>
            </div>
          </div>
        </section>

        {/* Section 4: Forensic Intel (Judicial Scrubbing) */}
        <section className="py-[30vh] border-t border-white/5 bg-zinc-900/5 relative overflow-hidden">
          <div className="max-w-5xl mx-auto space-y-20">
            <header className="space-y-6">
              <h2 className="text-[var(--text-h2)]">
                Forensic <br />Intel.
              </h2>
              <p className="text-[var(--text-body)] text-zinc-400">
                Scale without privacy rot. 100% local AST parsing ensures zero PII egress via <span className="text-white">Judicial Scrubbing</span>.
              </p>
            </header>

            <div className="flex flex-col md:flex-row gap-24 items-center">
              <div className="flex-1 space-y-12">
                <div className="space-y-4">
                  <h3 className="text-xs font-black uppercase tracking-[0.4em] text-zinc-600">Performance Benchmark</h3>
                  <div className="text-5xl font-black italic tracking-tighter">&lt;110ms</div>
                  <p className="text-xs text-zinc-500">Forensic latency for 10M+ node architectural queries.</p>
                </div>
              </div>

              <div className="flex-1 p-16 border border-white/10 bg-black">
                <div className="font-mono text-[11px] space-y-4">
                  <div className="text-emerald-truth">PRIME_ENGINE_READY</div>
                  <div className="text-zinc-500">Scanning filesystem heartbeat...</div>
                  <div className="text-zinc-500">PII_FILTER_ACTIVE: AES-256</div>
                  <div className="text-white border-t border-white/10 pt-4 mt-4">REGISTRY_INTEGRITY: SEALED</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Section 5: Establishment (Installation) */}
        <section id="install" className="py-[30vh] border-t border-white/5">
          <div className="max-w-3xl mx-auto text-center space-y-24">
            <h2 className="text-[var(--text-h2)]">
              Establish the <br />Registry.
            </h2>

            <div className="space-y-12">
              <div className="p-16 border border-white/10 bg-black flex justify-between items-center group cursor-pointer hover:border-emerald-truth transition-all">
                <div className="text-left space-y-2">
                  <span className="text-[10px] font-black uppercase tracking-[0.4em] text-zinc-700">Protocol 01</span>
                  <div className="text-2xl font-black italic">pip install sidelith</div>
                </div>
                <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="h-6 w-6 bg-emerald-truth rounded-sm" />
                </div>
              </div>

              <div className="p-16 border border-white/10 bg-black flex justify-between items-center">
                <div className="text-left space-y-2">
                  <span className="text-[10px] font-black uppercase tracking-[0.4em] text-zinc-700">Protocol 02</span>
                  <div className="text-2xl font-black italic text-zinc-500">{`"sidelith": { "command": "python" }`}</div>
                </div>
              </div>
            </div>

            <div className="pt-12">
              <Link href="/login" className="h-24 px-20 bg-white text-black font-black text-3xl uppercase italic tracking-tighter font-heading hover:bg-zinc-200 transition-all flex items-center justify-center gap-6 shadow-[0_0_80px_rgba(255,255,255,0.1)]">
                Claim Your Side <ChevronRight className="w-10 h-10" />
              </Link>
            </div>
          </div>
        </section>

        {/* Footer: Judicial Ledger */}
        <footer className="py-24 border-t border-white/10 bg-black">
          <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-start gap-24">
            <div className="space-y-8">
              <div className="flex items-center gap-4">
                <div className="h-8 w-8 bg-white rounded-sm" />
                <span className="font-black text-3xl tracking-tighter uppercase italic text-white font-heading">Sidelith</span>
              </div>
              <p className="text-[11px] font-black uppercase tracking-[0.5em] text-zinc-700 max-w-sm">
                System of Record for Sovereign Engineering.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-24 text-[11px] font-black uppercase tracking-[0.4em] text-zinc-600">
              <div className="space-y-4 flex flex-col">
                <Link href="#logic" className="hover:text-white transition-colors">Forensics</Link>
                <Link href="#install" className="hover:text-white transition-colors">Install</Link>
                <Link href="/pricing" className="hover:text-white transition-colors">Sovereignty</Link>
              </div>
              <div className="space-y-4 flex flex-col">
                <Link href="https://github.com/erhan-github/side" className="hover:text-white transition-colors">GitHub</Link>
                <Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link>
              </div>
            </div>
          </div>
          <div className="max-w-7xl mx-auto px-6 mt-32 pt-12 border-t border-white/5 flex flex-col md:flex-row justify-between items-center text-[9px] text-zinc-900 font-black uppercase tracking-[0.6em] gap-8">
            <div>© 2026 Sovereign Strategic Intelligence Group</div>
            <div className="flex gap-12">
              <span>Universal Integrity Enforced</span>
              <span>AES-256 Vaulted</span>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}

const ExternalLink = ({ className }: { className?: string }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
    <polyline points="15 3 21 3 21 9" />
    <line x1="10" y1="14" x2="21" y2="3" />
  </svg>
);
