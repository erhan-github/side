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
            <Link href="/login" className="flex items-center gap-2 text-white bg-white/10 px-5 py-2 rounded-full hover:bg-white/20 transition-all font-bold border border-white/5 uppercase tracking-widest text-[10px]">
              Authenticate <ChevronRight className="w-3 h-3" />
            </Link>
          </div>
        </div>
      </nav>

      <main>
        {/* Hero */}
        <section className="min-h-[85vh] flex flex-col items-center justify-center text-center px-6 pt-32 pb-24">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 text-xs text-zinc-400 mb-6 hover:bg-white/10 transition-colors cursor-default">
            <Zap className="w-3 h-3 text-yellow-400" />
            <span>The Strategic Kernel • Works alongside Cursor, Windsurf, Claude</span>
          </div>

          <h1 className="text-[var(--text-hero)] font-black uppercase italic leading-[0.8] max-w-7xl font-heading mb-[var(--space-md)]">
            The Side.
          </h1>
          <p className="text-[var(--text-body)] text-zinc-400 max-w-2xl mx-auto leading-relaxed font-sans mb-[var(--space-md)]">
            Side is the **Sovereign Registry** for the modern stack.
            The essential strategic layer that bridges Cursor, Windsurf, and Claude.
          </p>
          <div className="flex items-center justify-center gap-12 text-[11px] font-black uppercase tracking-[0.4em] text-emerald-500/40 opacity-60 mb-[var(--space-lg)]">
            <span>Deterministic Memory</span>
            <span>Trajectory Guard</span>
            <span>Universal Sync</span>
          </div>

          <div className="flex flex-col items-center gap-8">
            <div className="flex flex-col md:flex-row items-center gap-6">
              <div className="group relative">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full blur opacity-20 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
                <button
                  onClick={handleCopy}
                  className="relative h-16 pl-8 pr-6 rounded-full bg-emerald-500 text-black font-black hover:bg-emerald-400 transition-all flex items-center gap-3 text-lg uppercase italic tracking-tighter font-heading shadow-[0_0_20px_rgba(16,185,129,0.3)]"
                >
                  <Terminal className="w-5 h-5 text-black" />
                  <span className="font-mono tracking-tight mr-2">pip install sidelith</span>
                  {copied ? (
                    <div className="bg-white text-black text-[10px] px-2 py-1 rounded-full flex items-center gap-1 animate-in fade-in slide-in-from-left-2 uppercase font-black">
                      <Check className="w-3 h-3" /> Initialized
                    </div>
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-black/10 flex items-center justify-center group-hover:bg-black/20 transition-colors">
                      <Copy className="w-4 h-4 text-black" />
                    </div>
                  )}
                </button>
              </div>

              <Link
                href="/login"
                className="h-16 px-10 rounded-full border border-white/10 bg-black flex items-center justify-center font-black hover:bg-emerald-500/10 hover:border-emerald-500/30 hover:text-emerald-400 transition-all group uppercase tracking-widest text-sm italic font-heading"
              >
                Authenticate Protocol <ChevronRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>

            <div className="flex flex-wrap justify-center gap-8 text-[10px] font-black uppercase tracking-[0.2em] text-zinc-600">
              <div className="flex items-center gap-2">
                <div className="w-1 h-1 rounded-full bg-emerald-500" />
                <span>Forensic Sync: ACTIVE</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1 h-1 rounded-full bg-blue-500" />
                <span>Local Encryption: AES-256</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1 h-1 rounded-full bg-zinc-700" />
                <span>Registry: Sealed</span>
              </div>
            </div>
          </div>

          <div className="absolute bottom-10 animate-bounce text-zinc-600">
            <ChevronDown className="w-6 h-6 opacity-50" />
          </div>
        </section>

        {/* Integration Marquee */}
        <section className="py-[var(--space-lg)] border-y border-white/5 bg-zinc-900/10">
          <div className="max-w-7xl mx-auto px-6">
            <p className="text-[10px] font-black uppercase tracking-[0.5em] text-zinc-600 text-center mb-10">Essential Integrated Pair</p>
            <div className="flex flex-wrap justify-center items-center gap-16 md:gap-24 opacity-40 grayscale hover:grayscale-0 transition-all duration-700">
              <div className="flex items-center gap-2 text-xl font-bold tracking-tighter text-white">
                <div className="w-5 h-5 bg-white rounded-md" /> Cursor
              </div>
              <div className="flex items-center gap-2 text-xl font-bold tracking-tighter text-white">
                <div className="w-5 h-5 bg-blue-500 rounded-md" /> Windsurf
              </div>
              <div className="flex items-center gap-2 text-xl font-bold tracking-tighter text-white">
                <div className="w-5 h-5 bg-[#D97757] rounded-md" /> Claude
              </div>
              <div className="flex items-center gap-2 text-xl font-bold tracking-tighter text-white">
                <div className="w-5 h-5 bg-zinc-800 rounded-md" /> GitHub
              </div>
              <div className="flex items-center gap-2 text-xl font-bold tracking-tighter text-white">
                <div className="w-5 h-5 bg-emerald-500 rounded-md" /> Vercel
              </div>
            </div>
          </div>
        </section>

        {/* Stats */}
        <section className="py-[var(--space-lg)]">
          <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4 px-6">
            <div className="p-8 bg-zinc-900/40 rounded-[2rem] border border-white/5 backdrop-blur-3xl">
              <p className="text-4xl font-black text-white italic tracking-tighter font-heading mb-1">42h</p>
              <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-bold">Rework Saved</p>
            </div>
            <div className="p-8 bg-zinc-900/40 rounded-[2rem] border border-white/5 backdrop-blur-3xl">
              <p className="text-4xl font-black text-white italic tracking-tighter font-heading mb-1">400st</p>
              <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-bold">Strategic IQ</p>
            </div>
            <div className="p-8 bg-emerald-500/5 rounded-[2rem] border border-emerald-500/10 backdrop-blur-3xl">
              <p className="text-4xl font-black text-emerald-400 italic tracking-tighter font-heading mb-1">100%</p>
              <p className="text-[10px] uppercase tracking-widest text-emerald-500/60 font-bold">Registry Integrity</p>
            </div>
            <div className="p-8 bg-zinc-900/40 rounded-[2rem] border border-white/5 backdrop-blur-3xl">
              <p className="text-4xl font-black text-white italic tracking-tighter font-heading mb-1">MIT</p>
              <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-bold">Open Context</p>
            </div>
          </div>
        </section>



        {/* The Sovereign Trust Protocol */}
        <section id="trust" className="py-[var(--space-xl)] px-6 border-y border-white/5 bg-zinc-900/40">
          <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-24 items-center">
            <div className="space-y-8">
              <h2 className="text-[var(--text-h2)] font-black uppercase italic leading-none font-heading">
                The Sovereign<br />Trust Protocol.
              </h2>
              <p className="text-[var(--text-body)] text-zinc-400 leading-relaxed font-sans">
                Side is built on deterministic truth. We don&apos;t ask for your trust; we prove it through architectural transparency.
              </p>
              <div className="space-y-6 pt-4">
                {[
                  { title: "Zero-Keylogging", desc: "We monitor filesystem events, not keystrokes. Side only hears what you commit to disk.", icon: Shield },
                  { title: "Manual Trigger", desc: "No autonomous code mutation. Every fix requires a deliberate user action and explicit approval.", icon: Lock },
                  { title: "Local Sovereignty", desc: "100% of code parsing happens on your machine. We sync structural metadata, never your source code.", icon: Globe }
                ].map((item, i) => (
                  <div key={i} className="flex gap-4 group">
                    <div className="mt-1 p-2 rounded-lg bg-emerald-500/5 border border-emerald-500/10 text-emerald-500 group-hover:bg-emerald-500/10 transition-colors">
                      <item.icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-white font-bold uppercase tracking-tight text-sm mb-1">{item.title}</h3>
                      <p className="text-zinc-500 text-sm leading-relaxed">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative group">
              <div className="absolute -inset-4 bg-emerald-500/5 blur-3xl opacity-50 group-hover:opacity-100 transition-opacity" />
              <div className="relative p-12 rounded-[2.5rem] bg-zinc-900/50 border border-white/5 backdrop-blur-3xl">
                <div className="space-y-6 font-mono text-xs">
                  <div className="flex items-center justify-between text-emerald-500/40 uppercase tracking-widest font-black">
                    <span>Protocol Status</span>
                    <span>v1.0.4</span>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-zinc-500">
                      <span>Filesystem Monitor</span>
                      <span className="text-emerald-500 font-bold">ACTIVE</span>
                    </div>
                    <div className="flex justify-between text-zinc-500">
                      <span>AES-256 Encryption</span>
                      <span className="text-emerald-500 font-bold">ENFORCED</span>
                    </div>
                    <div className="flex justify-between text-zinc-500">
                      <span>Cloud PII Scrubbing</span>
                      <span className="text-emerald-500 font-bold">MANDATORY</span>
                    </div>
                  </div>
                  <div className="h-px bg-white/5" />
                  <div className="text-[10px] text-zinc-600 italic leading-relaxed">
                    &quot;The user remains the final authority. Logic drift is flagged, never autonomous.&quot;
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Sovereign Integrity (Values) */}
        <section className="py-[var(--space-xl)] px-6 bg-black relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(16,185,129,0.05),transparent)] pointer-events-none" />
          <div className="max-w-6xl mx-auto relative z-10">
            <div className="text-center mb-[var(--space-lg)]">
              <h2 className="text-[var(--text-h2)] font-black uppercase italic mb-[var(--space-sm)]">Sovereign Integrity.</h2>
              <p className="text-[11px] text-zinc-500 uppercase tracking-[0.4em] font-black">Built on deterministic Truth, not generative guesses.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-[var(--space-md)]">
              <div className="p-[var(--space-md)] rounded-[2.5rem] bg-zinc-900/20 border border-white/5 group hover:border-emerald-500/20 transition-all">
                <div className="h-1 w-12 bg-emerald-500 mb-6 group-hover:w-20 transition-all" />
                <h3 className="text-2xl font-black uppercase italic mb-4">The Logic Guard</h3>
                <p className="text-zinc-400 text-sm leading-relaxed mb-6">
                  Sidelith monitors the **Invisible Why**. When you close your IDE, your architectural intent is secured in the Registry.
                </p>
                <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest text-[#10b981]">
                  <span>Registry: Active</span>
                  <span className="opacity-40">IQ: 400st</span>
                </div>
              </div>

              <div className="p-[var(--space-md)] rounded-[2.5rem] bg-zinc-900/20 border border-white/5 group hover:border-blue-500/20 transition-all">
                <div className="h-1 w-12 bg-blue-500 mb-6 group-hover:w-20 transition-all" />
                <h3 className="text-2xl font-black uppercase italic mb-4">System of Record</h3>
                <p className="text-zinc-400 text-sm leading-relaxed mb-6">
                  Editors manage text. Agents manage action. Side manages **Truth**. The immutable ledger for project trajectory.
                </p>
                <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest text-blue-400">
                  <span>Ledger: Immutable</span>
                  <span className="opacity-40">AES-256</span>
                </div>
              </div>

              <div className="p-[var(--space-md)] rounded-[2.5rem] bg-zinc-900/20 border border-white/5 group hover:border-purple-500/20 transition-all">
                <div className="h-1 w-12 bg-purple-500 mb-6 group-hover:w-20 transition-all" />
                <h3 className="text-2xl font-black uppercase italic mb-4">Forensic Intel</h3>
                <p className="text-zinc-400 text-sm leading-relaxed mb-6">
                  Scale without privacy rot. 100% local AST parsing ensures zero PII egress via **Judicial Scrubbing**.
                </p>
                <div className="flex justify-between items-center text-[10px] font-black uppercase tracking-widest text-purple-400">
                  <span>Scrub: Enforced</span>
                  <span className="opacity-40">&lt;110ms</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Trajectory Protection (Storytelling) */}
        <section className="py-[var(--space-xl)] px-6 relative overflow-hidden bg-zinc-900/10 border-y border-white/5">
          <div className="max-w-5xl mx-auto font-sans">
            <div className="text-center mb-[var(--space-lg)]">
              <h2 className="text-[var(--text-h2)] font-black uppercase italic leading-[0.9] mb-[var(--space-sm)] font-heading">
                Protect the <br />Trajectory.
              </h2>
              <p className="text-[var(--text-body)] text-zinc-500 max-w-xl mx-auto uppercase tracking-[0.2em] text-[10px] font-black">
                Projects don&apos;t fail from lack of code. They fail from loss of intent.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-[var(--space-md)] max-w-4xl mx-auto">
              <div className="p-10 rounded-[2.5rem] bg-zinc-900/30 border border-white/5 space-y-6">
                <div className="flex justify-between items-center opacity-40">
                  <span className="text-[10px] font-black uppercase tracking-widest text-red-500">Normal Engineering</span>
                  <span className="text-[10px] font-mono">0.4x Leverage</span>
                </div>
                <div className="space-y-4">
                  <div className="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full bg-red-800 w-[30%]" />
                  </div>
                  <p className="text-[10px] text-zinc-600 uppercase font-black">Context Retention</p>
                </div>
                <p className="text-sm text-zinc-500 italic leading-relaxed">
                  &quot;Six months later, nobody remembers why we chose this auth pattern. The team refactors, breaks dependencies, and loses 40 hours to context recovery.&quot;
                </p>
              </div>

              <div className="p-10 rounded-[2.5rem] bg-emerald-500/5 border border-emerald-500/10 space-y-6 relative group overflow-hidden">
                <div className="absolute top-0 right-0 p-8 opacity-20 group-hover:opacity-100 transition-opacity">
                  <Shield className="w-8 h-8 text-emerald-400" />
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-[10px] font-black uppercase tracking-widest text-emerald-500">Sovereign Registry</span>
                  <span className="text-[10px] font-mono text-emerald-400 font-bold text-base">4.2x Leverage</span>
                </div>
                <div className="space-y-4">
                  <div className="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500 w-full animate-pulse" />
                  </div>
                  <p className="text-[10px] text-emerald-500/60 uppercase font-black tracking-widest">100% Intent Preservation</p>
                </div>
                <p className="text-sm text-zinc-300 font-medium leading-relaxed">
                  &quot;Hey Side, why JWTs?&quot; — Side recalls the strategic rationale instantly, audits the implementation, and prevents the rework before a single line is broken.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* The Silent Observer */}
        <section className="py-[var(--space-xl)] px-6 bg-black relative overflow-hidden">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-blue-500/50 to-transparent" />
          <div className="max-w-6xl mx-auto">
            <div className="flex flex-col md:flex-row items-center gap-24 font-sans">
              <div className="flex-1 space-y-8">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-blue-500/20 bg-blue-500/10 text-[10px] text-blue-400 font-black uppercase tracking-widest">
                  Zero Distraction Engine
                </div>
                <h2 className="text-[var(--text-h2)] font-black uppercase italic leading-[0.9] font-heading">
                  The Silent <br />Observer.
                </h2>
                <p className="text-[var(--text-body)] text-zinc-400 leading-relaxed max-w-xl">
                  Side doesn&apos;t ask for your attention. It earns it.
                  Passively monitoring the filesystem heartbeat, only surfacing when your trajectory deviates from the **Sovereign Path**.
                </p>
                <div className="grid grid-cols-2 gap-12 pt-4">
                  <div className="space-y-3">
                    <p className="text-[10px] font-black uppercase text-blue-500 tracking-[0.3em] italic">01. Instrumentation</p>
                    <p className="text-sm text-zinc-500 leading-relaxed font-medium">Autonomous audit of every file save event. Zero-latency context hydration.</p>
                  </div>
                  <div className="space-y-3">
                    <p className="text-[10px] font-black uppercase text-emerald-400 tracking-[0.3em] italic">02. Deterministic Probes</p>
                    <p className="text-sm text-zinc-500 leading-relaxed font-medium">No magic. We flag logic drift using multi-pass Tree-Sitter forensic probes.</p>
                  </div>
                </div>
              </div>

              <div className="flex-1 w-full max-w-md p-10 rounded-[2.5rem] bg-zinc-900/50 border border-white/5 relative group transition-all duration-700 hover:border-blue-500/30 backdrop-blur-3xl">
                <div className="absolute inset-0 bg-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-[2.5rem]" />
                <div className="relative z-10 space-y-8 font-mono">
                  <div className="flex justify-between items-center pb-6 border-b border-white/5">
                    <span className="text-[10px] font-black uppercase tracking-[0.2em] text-[#a1a1a1]">Watcher Heartbeat</span>
                    <span className="text-[10px] text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 uppercase tracking-tighter">T3_SYNC</span>
                  </div>
                  <div className="space-y-4">
                    <div className="flex justify-between text-[11px] font-medium tracking-tight">
                      <span className="text-zinc-500 uppercase font-black">Leverage Index</span>
                      <span className="text-white italic font-black">2.44x [ROI]</span>
                    </div>
                    <div className="h-2 w-full bg-zinc-950 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 w-[60%] transition-all duration-1000 group-hover:w-[85%]" />
                    </div>
                  </div>
                  <div className="pt-6 space-y-4 border-t border-white/5">
                    <div className="space-y-3">
                      <div className="text-[10px] text-zinc-300 flex items-center justify-between font-bold uppercase tracking-widest">
                        <span>Logic Stability</span>
                        <span className="text-emerald-400">98.2%</span>
                      </div>
                      <div className="text-[10px] text-zinc-300 flex items-center justify-between font-bold uppercase tracking-widest">
                        <span>Drift Neutralization</span>
                        <span className="text-blue-400">ENFORCED</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Case Logs - Forensic Evidence */}
        <section id="caselogs" className="py-[var(--space-xl)] px-6 border-t border-white/5 bg-black">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-[var(--text-h2)] font-black uppercase italic leading-[0.9] text-center mb-[var(--space-sm)] font-heading">
              Forensic Evidence.
            </h2>
            <p className="text-[var(--text-body)] text-zinc-500 text-center mb-[var(--space-lg)] max-w-2xl mx-auto uppercase tracking-[0.2em] text-[10px] font-black">
              When Side saves you from a 2-week mistake, it pays for itself forever.
            </p>

            <div className="bg-zinc-900/30 rounded-[2.5rem] border border-white/10 overflow-hidden backdrop-blur-3xl shadow-2xl">
              <div className="grid grid-cols-1 md:grid-cols-12 min-h-[600px]">
                {/* Left: Tabs */}
                <div className="md:col-span-4 border-r border-white/10 bg-black/40">
                  <div className="p-6 space-y-3">
                    {[
                      { id: "auth", icon: Shield, label: "Isomorphic Drift", save: "Fixed Hydration" },
                      { id: "research", icon: Globe, label: "Cost Forensics", save: "Saved $4.2k/mo" },
                      { id: "fork", icon: Brain, label: "Recursive Macros", save: "AST Precision" },
                      { id: "pivot", icon: FileText, label: "SOC2 Compliance", save: "Audited Thread" },
                      { id: "scale", icon: Zap, label: "Cold Start Debt", save: "< 200ms TTFT" },
                      { id: "sec", icon: Eye, label: "Judicial Scrub", save: "Zero PII Egress" }
                    ].map((tab) => (
                      <button
                        key={tab.id}
                        onClick={() => setActiveCase(tab.id)}
                        className={`w-full text-left px-5 py-5 rounded-2xl transition-all duration-300 flex items-center justify-between border ${activeCase === tab.id
                          ? "bg-white/10 border-white/10 text-white shadow-xl translate-x-1"
                          : "border-transparent text-zinc-500 hover:text-zinc-300 hover:bg-white/5"
                          }`}
                      >
                        <div className="flex items-center gap-4">
                          <tab.icon className={`w-4 h-4 ${activeCase === tab.id ? "text-emerald-400" : "text-zinc-700"}`} />
                          <span className="font-bold text-xs uppercase tracking-tighter italic font-heading">{tab.label}</span>
                        </div>
                        <span className={`text-[9px] font-black px-2 py-0.5 rounded border uppercase italic tracking-widest ${activeCase === tab.id
                          ? "bg-emerald-500 text-black border-emerald-500"
                          : "bg-zinc-800 border-zinc-700 opacity-20"
                          }`}>
                          {tab.save}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Right: Visual */}
                <div className="md:col-span-8 bg-black/60 p-8 md:p-12 flex flex-col relative overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 via-blue-500/5 to-transparent pointer-events-none" />

                  <div className="flex items-center justify-between mb-10 relative z-10">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full animate-pulse bg-emerald-500`} />
                      <span className="text-[10px] font-black uppercase tracking-[0.3em] text-zinc-500">Forensic Thread: T3_SYNC</span>
                    </div>
                  </div>

                  <div className="flex-grow space-y-8 relative z-10 font-sans">
                    <div className="flex justify-end">
                      <div className="bg-blue-600 text-white px-6 py-5 rounded-[2rem] rounded-br-none text-sm max-w-[85%] shadow-2xl font-medium leading-relaxed">
                        {activeCase === 'auth' && "Logic thread Jan14 flagged for hydration drift. Side detected SSR/HMR cache mismatch in Server Actions."}
                        {activeCase === 'research' && "LLM Cost Forecast: Reasoning threads on 70B yielding <30% accuracy. Recommend escalation to 405B?"}
                        {activeCase === 'fork' && "Multi-pass analysis stalling at depth 4 in Rust macros. Request deep recursive scan for intent anchor?"}
                        {activeCase === 'pivot' && "Strategy Audit: SOC2 Type 2 compliance requires definitive Judicial integrity in project log sinks."}
                        {activeCase === 'scale' && "Forensic TTFT Alert: Cold starts in Server Actions hitting 1.2s. Potential for cache hydration optimization?"}
                        {activeCase === 'sec' && "Registry Scan: Found raw PII in webhook debug logs. Enable forensic masking protocol?"}
                      </div>
                    </div>

                    <div className="flex justify-start">
                      <div className="bg-zinc-900 border border-white/10 px-8 py-6 rounded-[2rem] rounded-bl-none max-w-[95%] shadow-2xl">
                        <div className="font-mono text-sm leading-relaxed">
                          {activeCase === 'auth' && (
                            <>
                              <p className="text-emerald-400 font-black mb-4 flex items-center gap-2 uppercase tracking-widest"><Shield className="w-4 h-4" /> Forensic Resolution</p>
                              <p className="text-zinc-300 mb-4">Hydration mismatch in `logic_thread_09`. SSR cache flush required to prevent trajectory drift.</p>
                              <div className="bg-black/50 p-4 rounded-xl border border-white/5 mb-4 group hover:border-emerald-500/20 transition-all">
                                <p className="text-emerald-500/60 text-[10px] uppercase font-black mb-2 tracking-widest italic">Correction Applied:</p>
                                <code className="text-[12px] text-emerald-400 font-bold">{`export const dynamic = 'force-dynamic';\n// Drift neutralized.`}</code>
                              </div>
                              <p className="text-zinc-600 text-[10px] font-black uppercase tracking-[0.3em] pl-4 border-l-2 border-emerald-500/20">
                                System IQ Impact: +12 Points
                              </p>
                            </>
                          )}

                          {activeCase === 'research' && (
                            <>
                              <div className="text-[11px] text-zinc-300 leading-relaxed italic border-l-2 border-cyan-500/20 pl-4 py-1">
                                &quot;PII from customer sessions is currently flowing into local logs. This violates the 'Sealed Registry' constraint for Enterprise Tier.&quot;
                              </div>
                              <p className="text-emerald-400 font-black mt-4 text-[10px] flex items-center gap-1 uppercase tracking-widest underline underline-offset-4">
                                <Check className="w-3 h-3" /> Fix Applied: Judicial Scrubbing enabled.
                              </p>
                            </>
                          )}

                          {(activeCase !== 'auth' && activeCase !== 'research') && (
                            <>
                              <p className="text-blue-400 font-black mb-4 flex items-center gap-2 uppercase tracking-widest"><RefreshCw className="w-4 h-4" /> Forensic Thread</p>
                              <p className="text-zinc-300">Context hydration active. Registry maintaining 100% integrity across this strategic bridge.</p>
                            </>
                          )}

                          {/* COLD START CONTENT */}
                          {activeCase === 'scale' && <>
                            <p className="text-yellow-400 font-black mb-3 flex items-center gap-2"><Zap className="w-4 h-4" /> ⚠️ INFRASTRUCTURE DEBT</p>
                            <p className="text-white mb-3">Cold start latency in Server Actions exceeds 800ms. TTFT budget violated.</p>
                            <div className="bg-black/30 p-4 rounded border border-white/5 mb-3 space-y-3">
                              <div className="flex justify-between text-[11px]">
                                <span className="text-zinc-500 uppercase font-black">Current TTFT</span>
                                <span className="text-red-400 font-bold">1.2s (Forensic Failure)</span>
                              </div>
                              <div className="flex justify-between text-[11px]">
                                <span className="text-white font-black uppercase">Optimized Target</span>
                                <span className="text-emerald-400 font-bold">&lt; 110ms (Sidelith Tier)</span>
                              </div>
                            </div>
                            <p className="text-zinc-500 text-[10px] font-black uppercase tracking-widest">
                              Recommendation: Direct deployment to Vercel/Railway Edge or enable Isomorphic Caching.
                            </p>
                          </>}

                          {/* JUDICIAL SCRUB CONTENT */}
                          {activeCase === 'sec' && <>
                            <p className="text-orange-400 font-black mb-3 flex items-center gap-2"><Eye className="w-4 h-4" /> 🔍 JUDICIAL SCRUBBING AUDIT</p>
                            <p className="text-white mb-3">Potential PII Egress detected in `lemonsqueezy_webhook.py` logic thread. Registry at risk.</p>
                            <div className="font-mono text-[10px] bg-black p-4 rounded border border-red-500/30 text-red-300 mb-3 overflow-x-auto leading-relaxed">
                              {`[FORENSICS] Scanning line 42...\n[ALERT] Customer email 'e.erdogan@...' found in raw debug logs.\n[ACTION] Forensic Masking applied. Judicial sync secured.`}
                            </div>
                            <p className="text-emerald-400 text-[10px] font-black mt-2 border-t border-white/10 pt-2 uppercase tracking-widest">
                              Registry Status: 100% CLEAN. Integrity preserved.
                            </p>
                          </>}

                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </section >

        {/* The Strategic Brain - MONOLITH.md Mock */}
        <section className="py-24 px-4 md:px-6 border-t border-white/10 bg-[#0c0c0e] relative overflow-hidden">
          <div className="max-w-[1200px] mx-auto relative z-10">
            <div className="text-center mb-10">
              <h2 className="text-4xl md:text-5xl font-black tracking-tight mb-4 text-white uppercase italic font-heading">Deterministic Architecture.</h2>
              <p className="text-xl text-zinc-400 max-w-2xl mx-auto uppercase tracking-[0.2em] text-[10px] font-black font-sans">
                Side maintains the ground-truth in a local <code className="text-emerald-400 bg-white/5 px-2 py-0.5 rounded border border-emerald-500/10 font-bold lowercase">MONOLITH.md</code>.
              </p>
            </div>

            {/* IDE Container */}
            <div className="rounded-lg border border-white/10 bg-[#1e1e1e] shadow-2xl overflow-hidden font-mono text-sm relative flex flex-col h-[700px] max-h-[80vh] ring-1 ring-black/50">
              {/* Title Bar */}
              <div className="h-9 bg-[#3c3c3c] flex items-center justify-between px-3 select-none border-b border-[#2b2b2b]">
                <div className="flex items-center gap-1.5 opacity-60">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
                </div>
                <div className="text-[#cccccc] text-xs flex items-center gap-2">
                  <span className="opacity-50">SIREN-LEDGER —</span>
                  <span className="font-bold">.side/MONOLITH.md</span>
                </div>
                <div className="w-10" />
              </div>

              <div className="flex flex-1 overflow-hidden">
                {/* Activity Bar */}
                <div className="w-10 bg-[#333333] flex flex-col items-center py-3 gap-4 border-r border-[#2b2b2b]">
                  <Copy className="w-5 h-5 text-white opacity-90" />
                  <Eye className="w-5 h-5 text-[#858585]" />
                  <Brain className="w-5 h-5 text-[#858585]" />
                </div>

                {/* Sidebar */}
                <div className="w-56 bg-[#252526] flex flex-col border-r border-[#2b2b2b] hidden md:flex text-[12px]">
                  <div className="h-8 flex items-center px-3 text-[#bbbbbb] font-bold uppercase tracking-wider text-[10px] opacity-80">Explorer</div>
                  <div className="pt-1">
                    <div className="flex items-center gap-1 px-1 py-0.5 text-[#cccccc] font-bold uppercase tracking-widest text-[10px]">
                      <ChevronDown className="w-3 h-3" /> SIREN-LEDGER
                    </div>
                    <div className="pl-3 mt-0.5 space-y-0.5 text-[#cccccc]">
                      <div className="flex items-center gap-1.5 px-2 py-0.5 opacity-60 hover:bg-[#2a2d2e] cursor-pointer">
                        <span>src</span>
                      </div>
                      <div className="flex items-center gap-1.5 px-2 py-0.5 opacity-60 hover:bg-[#2a2d2e] cursor-pointer">
                        <span>tests</span>
                      </div>
                      <div className="flex items-center gap-1.5 px-1 py-0.5 text-[#cccccc] font-bold mt-2">
                        <ChevronDown className="w-3 h-3 text-blue-400" /> .side
                      </div>
                      <div className="flex items-center gap-1.5 px-2 py-0.5 bg-[#37373d] text-white cursor-pointer -ml-3 pl-5 border-l-2 border-blue-500">
                        <FileText className="w-3 h-3 text-emerald-500" /> <span>MONOLITH.md</span>
                      </div>
                      <div className="flex items-center gap-1.5 px-2 py-0.5 opacity-60 hover:bg-[#2a2d2e] cursor-pointer">
                        <span className="text-zinc-500">pyproject.toml</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Editor Content */}
                <div className="flex-1 flex flex-col bg-[#1e1e1e]">
                  <div className="h-8 bg-[#252526] flex items-center">
                    <div className="h-full bg-[#1e1e1e] flex items-center gap-2 px-3 border-t border-blue-500 text-white text-xs pr-8 min-w-[120px]">
                      <FileText className="w-3 h-3 text-emerald-500" />
                      <span>MONOLITH.md</span>
                    </div>
                  </div>

                  <div className="flex-1 overflow-y-auto p-4 md:p-8 font-mono text-[13px] leading-relaxed text-[#d4d4d4] relative">
                    {/* Auto-Sync Badge */}
                    <div className="absolute top-4 right-4 bg-[#252526] border border-blue-500 shadow-xl p-3 rounded-md flex items-start gap-3 w-64 z-20">
                      <div className="mt-0.5 w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                      <div>
                        <h4 className="text-[10px] font-black text-blue-400 uppercase tracking-widest">Sidelith • Registry</h4>
                        <p className="text-[#a1a1a1] text-[10px]">Synchronized 40 decision nodes. <span className="text-white italic">Sealed.</span></p>
                      </div>
                    </div>

                    <div className="max-w-2xl bg-[#1e1e1e] rounded-lg">
                      <div className="flex justify-between items-center mb-10 border-b border-white/5 pb-4">
                        <div className="flex items-center gap-3">
                          <div className="w-1.5 h-6 bg-emerald-500 rounded-full" />
                          <h1 className="text-white font-black text-2xl uppercase italic tracking-tighter">PRIME_REGISTRY // V4.2</h1>
                        </div>
                        <div className="flex items-center gap-2 text-[9px] font-black text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20 uppercase tracking-widest">
                          <Lock className="w-3 h-3" /> Sealed Registry
                        </div>
                      </div>

                      <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-5 mb-10 relative group">
                        <div className="absolute -left-1 top-4 w-2 h-8 bg-emerald-500 rounded-full" />
                        <p className="text-zinc-500 text-[9px] mb-2 uppercase tracking-widest font-black opacity-70">STRATEGIC PROVOCATION Engine</p>
                        <p className="text-zinc-200 italic font-medium leading-relaxed text-[15px]">
                          &quot;Logic thread `thread_auth_sync` is currently suffering from context fragmentation. You are building for a multi-agent future, yet your state management remains isomorphic-only. Flatten the logic chain now or risk hydration debt in Q3.&quot;
                        </p>
                        <div className="mt-4 flex gap-2">
                          <span className="text-[9px] font-black bg-emerald-500 text-black px-1.5 py-0.5 rounded uppercase tracking-tighter">High ROI Action</span>
                          <span className="text-zinc-500 text-[9px] uppercase font-bold tracking-widest mt-0.5 hover:text-white cursor-pointer transition-colors">→ view forensic path</span>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-12 mb-12">
                        <div className="space-y-6">
                          <div className="text-zinc-400 border-b border-white/5 pb-2 flex items-center justify-between">
                            <strong className="text-white uppercase text-[10px] tracking-widest font-black">01_VITAL_FORENSICS</strong>
                            <span className="text-[10px] font-black text-emerald-400 underline italic tracking-tighter">IQ: 362/400</span>
                          </div>
                          <div className="space-y-4 text-[11px] font-mono">
                            <div className="flex justify-between items-center bg-white/5 p-2 rounded">
                              <span className="text-zinc-500 uppercase tracking-widest font-bold">Semantic Depth</span>
                              <span className="text-emerald-400 font-bold">✓ 94%</span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-zinc-500 uppercase tracking-widest">Logic Velocity</span>
                              <span className="text-emerald-400 font-bold">✓ STABLE</span>
                            </div>
                            <div className="flex justify-between items-center text-red-400 border-t border-white/5 pt-2">
                              <span className="text-zinc-400 uppercase tracking-widest">Context Drift</span>
                              <span className="font-bold underline decoration-red-500/50">! CRITICAL (Auth)</span>
                            </div>
                          </div>
                        </div>

                        <div className="space-y-6">
                          <div className="text-zinc-400 border-b border-white/5 pb-2">
                            <strong className="text-white uppercase text-[10px] tracking-widest font-black">02_FORENSIC_THREADS</strong>
                          </div>
                          <ul className="space-y-4 text-[11px]">
                            <li className="flex gap-3 group cursor-pointer">
                              <span className="w-4 h-4 rounded-sm bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold text-[10px]">T1</span>
                              <span className="text-zinc-400 group-hover:text-white transition-colors">Optimization: `rust_macros_v2`</span>
                            </li>
                            <li className="flex gap-3 group cursor-pointer">
                              <span className="w-4 h-4 rounded-sm bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-[10px]">T2</span>
                              <span className="text-zinc-400 group-hover:text-white transition-colors">Judicial Scrub: `payment_webhooks`</span>
                            </li>
                            <li className="flex gap-3 group cursor-pointer">
                              <span className="w-4 h-4 rounded-sm bg-yellow-500/20 text-yellow-400 flex items-center justify-center font-bold text-[10px]">T3</span>
                              <span className="text-white font-bold italic tracking-tighter">Fix Drift: `isomorphic_state_sync`</span>
                            </li>
                          </ul>
                        </div>
                      </div>

                      {/* MCP Button Mock */}
                      {/* Cursor Chat Mock Widget */}
                      <div className="mt-16 absolute bottom-10 right-8 w-80 bg-[#252526] border border-blue-500/50 rounded-xl shadow-[0_20px_60px_-10px_rgba(0,0,0,0.8)] overflow-hidden animate-in fade-in slide-in-from-bottom-10 duration-700">
                        <div className="h-8 bg-[#3c3c3c] flex items-center justify-between px-3 border-b border-[#2b2b2b]">
                          <span className="text-[10px] font-black uppercase tracking-widest text-[#a1a1a1]">Cursor Chat // AI Strategy</span>
                          <X className="w-3 h-3 text-zinc-500 cursor-pointer" />
                        </div>
                        <div className="p-4 space-y-4">
                          <div className="flex justify-end">
                            <div className="bg-blue-600 text-white p-3 rounded-lg rounded-br-none text-[11px] max-w-[90%] shadow-lg">
                              &quot;Hey Side, show me why the logic thread `T3` is drifting.&quot;
                            </div>
                          </div>
                          <div className="flex justify-start">
                            <div className="bg-[#1e1e1e] border border-white/10 p-3 rounded-lg rounded-bl-none text-[11px] text-zinc-300 shadow-xl leading-relaxed">
                              &quot;Analyzing `T3`... Sidelith found a hydration mismatch. Your client state is diverging from the server registry. <span className="text-emerald-400 font-bold">Fix applied: isomorphic-state-sync.</span>&quot;
                            </div>
                          </div>
                          <div className="pt-2 border-t border-white/5 flex gap-2">
                            <button className="flex-1 bg-emerald-500 text-black font-black text-[9px] py-2 rounded uppercase italic tracking-tighter">Finalize Forensic Node</button>
                            <button className="flex-1 bg-white/5 border border-white/10 text-white font-bold text-[9px] py-2 rounded uppercase tracking-widest">Ignore</button>
                          </div>
                        </div>
                      </div>

                      {/* Claude Code CLI Mock */}
                      <div className="absolute bottom-4 left-4 right-96 bg-black border border-white/5 p-3 rounded font-mono text-[10px] text-zinc-500 flex items-center gap-4 bg-opacity-80 backdrop-blur-sm">
                        <div className="flex items-center gap-2">
                          <Terminal className="w-3 h-3 text-emerald-500" />
                          <span className="text-emerald-300 font-bold">claude-code</span>
                          <span className="opacity-50 underline decoration-emerald-500/20 underline-offset-2 hover:opacity-100 cursor-pointer transition-opacity">sidelith --audit --thread T3</span>
                        </div>
                        <div className="h-3 w-px bg-white/10" />
                        <div className="flex items-center gap-2 opacity-60">
                          <Check className="w-3 h-3 text-emerald-500" />
                          <span>100% Forensic Integrity</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Status Bar */}
              <div className="h-6 bg-blue-600 flex items-center justify-between px-3 text-white text-[10px] select-none uppercase font-bold">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1"><GitBranch className="w-3 h-3" /> main*</div>
                  <div className="flex items-center gap-1 opacity-80"><RefreshCw className="w-3 h-3" /> sync complete</div>
                </div>
                <div className="flex items-center gap-4 opacity-75">
                  <span>UTF-8</span>
                  <span>Markdown</span>
                </div>
              </div>
            </div>
          </div>
        </section >

        {/* Installation Strategy */}
        <section id="install" className="py-[var(--space-md)] px-6 relative overflow-hidden border-t border-white/5 bg-zinc-900/10">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(16,185,129,0.05),transparent)] pointer-events-none" />
          <div className="max-w-4xl mx-auto py-24">
            <h2 className="text-[var(--text-h2)] font-black uppercase italic leading-[0.9] text-center mb-[var(--space-sm)] font-heading">
              Establish the <br />Registry.
            </h2>
            <p className="text-[var(--text-body)] text-zinc-500 text-center mb-[var(--space-lg)] uppercase tracking-[0.2em] text-[10px] font-black">
              Three commands to absolute architectural integrity.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-8 rounded-[2.5rem] bg-zinc-900/50 border border-white/5 space-y-6">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-white text-black font-black flex items-center justify-center text-sm font-heading">01</div>
                  <span className="font-black uppercase tracking-tighter text-white italic">Install</span>
                </div>
                <div className="bg-black/50 p-5 rounded-2xl border border-white/10 font-mono text-emerald-400 text-sm">
                  <code>pip install sidelith</code>
                </div>
              </div>

              <div className="p-8 rounded-[2.5rem] bg-zinc-900/50 border border-white/5 space-y-6">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-white text-black font-black flex items-center justify-center text-sm font-heading">02</div>
                  <span className="font-black uppercase tracking-tighter text-white italic">Hydrate</span>
                </div>
                <div className="bg-black/50 p-5 rounded-2xl border border-white/10 font-mono text-zinc-500 text-[11px] leading-relaxed">
                  <pre>{`"sidelith": {\n  "command": "python",\n  "args": ["-m", "side.server"]\n}`}</pre>
                </div>
              </div>

              <div className="p-8 rounded-[2.5rem] bg-zinc-900/50 border border-white/5 space-y-6">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-emerald-500 text-black font-black flex items-center justify-center text-sm font-heading">03</div>
                  <span className="font-black uppercase tracking-tighter text-white italic">Audit</span>
                </div>
                <div className="bg-emerald-500/5 p-5 rounded-2xl border border-emerald-500/10 font-mono text-emerald-400 text-sm italic">
                  <code>&quot;Hey Side, show drift.&quot;</code>
                </div>
              </div>
            </div>

            <div className="mt-20 text-center">
              <Link href="/login" className="h-20 px-16 rounded-full bg-white text-black font-black hover:bg-zinc-200 transition-all inline-flex items-center gap-3 text-2xl uppercase italic tracking-tighter shadow-2xl font-heading">
                Claim Your Side <ChevronRight className="w-8 h-8" />
              </Link>
            </div>
          </div>
        </section>

        {/* Global Technical Specs */}
        <section className="py-16 px-6 border-t border-white/5 bg-black">
          <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-12 text-center opacity-60">
            <div>
              <p className="text-3xl font-black text-white italic mb-1">100%</p>
              <p className="text-[9px] text-zinc-600 font-black uppercase tracking-[0.3em]">Judicial Sync</p>
            </div>
            <div>
              <p className="text-3xl font-black text-white italic mb-1">&lt;110ms</p>
              <p className="text-[9px] text-zinc-600 font-black uppercase tracking-[0.3em]">Forensic Latency</p>
            </div>
            <div>
              <p className="text-3xl font-black text-white italic mb-1">LOCAL</p>
              <p className="text-[9px] text-zinc-600 font-black uppercase tracking-[0.3em]">First Sovereignty</p>
            </div>
            <div>
              <p className="text-3xl font-black text-white italic mb-1">MIT</p>
              <p className="text-[9px] text-zinc-600 font-black uppercase tracking-[0.3em]">Open Context</p>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-24 px-6 border-t border-white/10 bg-black">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start gap-16 font-sans">
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <div className="h-6 w-6 bg-white rounded-sm" />
                <span className="font-black text-2xl tracking-tighter uppercase italic text-white font-heading underline decoration-white/20 underline-offset-4">Sidelith</span>
              </div>
              <p className="text-zinc-500 text-sm font-medium leading-relaxed max-w-sm">
                The Sovereign Registry for Project Context. <br />Professional-grade trajectory management for the modern engineering stack.
              </p>
            </div>

            <div className="flex gap-24 text-[11px] font-black uppercase tracking-[0.3em] text-zinc-400">
              <div className="flex flex-col gap-5">
                <Link href="#forensics" className="hover:text-white transition-colors">Forensics</Link>
                <Link href="#caselogs" className="hover:text-white transition-colors">Case Logs</Link>
                <Link href="#install" className="hover:text-white transition-colors">Install</Link>
                <Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link>
              </div>
              <div className="flex flex-col gap-5">
                <Link href="https://github.com/erhan-github/side" className="hover:text-white transition-colors flex items-center gap-2">GitHub <ExternalLink className="w-3 h-3 opacity-20" /></Link>
                <Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link>
                <Link href="/terms" className="hover:text-white transition-colors">Terms</Link>
              </div>
            </div>
          </div>
          <div className="max-w-7xl mx-auto mt-24 pt-10 border-t border-white/5 text-[9px] text-zinc-800 font-black uppercase tracking-[0.6em] text-center">
            © 2026 Sovereign Strategic Intelligence Group • Universal Project Sovereignty Enforced
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

