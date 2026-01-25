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

          <h1 className="text-7xl md:text-[10rem] font-black tracking-tighter mb-8 uppercase italic leading-[0.8] max-w-6xl font-heading text-white">
            Absolute<br />
            Integrity.
          </h1>
          <p className="text-2xl md:text-3xl text-zinc-400 mb-12 max-w-3xl mx-auto leading-tight font-medium font-sans">
            The professional <span className="text-white">System of Record</span> for modern engineering teams.
            Side protects your project trajectory where standard agents fail.
          </p>
          <div className="flex items-center justify-center gap-12 text-[10px] font-black uppercase tracking-[0.4em] text-emerald-500/60 mb-16">
            <span>Local-First</span>
            <span>Zero-Keylogging</span>
            <span>Sovereign Storage</span>
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

          <div className="mt-16 flex flex-col items-center gap-8 animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-200">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl">
              <div className="p-4 bg-zinc-900/50 rounded-2xl border border-white/5">
                <p className="text-3xl font-black text-white italic tracking-tighter">42h</p>
                <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-bold">Avg. Rework Saved</p>
              </div>
              <div className="p-4 bg-zinc-900/50 rounded-2xl border border-white/5">
                <p className="text-3xl font-black text-white italic tracking-tighter">400st</p>
                <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-bold">Strategic IQ Scale</p>
              </div>
              <div className="p-4 bg-zinc-900/50 rounded-2xl border border-white/5">
                <p className="text-3xl font-black text-white italic tracking-tighter">100%</p>
                <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-bold">Judicial Integrity</p>
              </div>
              <div className="p-4 bg-zinc-900/50 rounded-2xl border border-white/5">
                <p className="text-3xl font-black text-white italic tracking-tighter">MIT</p>
                <p className="text-[10px] uppercase tracking-widest text-zinc-500 font-bold">Open Registry</p>
              </div>
            </div>
          </div>
        </section>



        {/* The Sovereign Trust Protocol */}
        <section id="trust" className="py-32 px-6 border-y border-white/5 bg-zinc-900/[0.15]">
          <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-24 items-center">
            <div className="space-y-8">
              <h2 className="text-5xl font-black tracking-tighter uppercase italic leading-none font-heading text-white">
                The Sovereign<br />Trust Protocol.
              </h2>
              <p className="text-xl text-zinc-400 leading-relaxed font-sans">
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
              <div className="relative p-12 rounded-[2rem] bg-zinc-900/50 border border-white/5 backdrop-blur-3xl">
                <div className="space-y-6 font-mono text-xs">
                  <div className="flex items-center justify-between text-emerald-500/40 uppercase tracking-widest font-black">
                    <span>Protocol Status</span>
                    <span>v1.0.4</span>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-zinc-500">
                      <span>Filesystem Monitor</span>
                      <span className="text-emerald-500">ACTIVE</span>
                    </div>
                    <div className="flex justify-between text-zinc-500">
                      <span>AES-256 Encryption</span>
                      <span className="text-emerald-500">ENFORCED</span>
                    </div>
                    <div className="flex justify-between text-zinc-500">
                      <span>Cloud PII Scrubbing</span>
                      <span className="text-emerald-500">MANDATORY</span>
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

        {/* The Sovereign Tease */}
        <section className="py-32 px-6 bg-black relative overflow-hidden">
          <div className="absolute inset-x-0 h-px top-0 bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent" />
          <div className="max-w-4xl mx-auto text-center space-y-10">
            <h2 className="text-5xl md:text-7xl font-black tracking-tighter uppercase italic leading-[0.9] font-heading">
              &quot;I already saw you<br />nesting those if-statements.&quot;
            </h2>
            <p className="text-2xl text-zinc-400 font-medium max-w-2xl mx-auto leading-snug font-sans">
              Side doesn&apos;t wait for help tickets. It detected your <span className="text-emerald-400">Logic Anomaly</span> 400ms after save.
              The refactor is ready when you are.
            </p>
            <div className="pt-8 flex justify-center gap-16 text-[10px] font-black uppercase tracking-[0.4em] text-zinc-600">
              <span className="flex items-center gap-2 border-b border-white/5 pb-2 hover:text-emerald-500 transition-colors cursor-default"><Eye className="w-3 h-3" /> Passive Observation</span>
              <span className="flex items-center gap-2 border-b border-white/5 pb-2 hover:text-emerald-500 transition-colors cursor-default"><Shield className="w-3 h-3" /> Zero Distraction</span>
              <span className="flex items-center gap-2 border-b border-white/5 pb-2 hover:text-emerald-500 transition-colors cursor-default"><Zap className="w-3 h-3" /> Instant Memory</span>
            </div>
          </div>
        </section>

        {/* The Forensics (Formerly Difference) */}
        <section id="forensics" className="py-20 px-6 border-t border-white/10">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-4xl font-black tracking-tighter text-center mb-12 uppercase italic">Deterministic Dominance</h2>

            <div className="flex flex-wrap justify-center gap-4 mb-16">
              {[
                { label: "IDE (Execution)", value: "Cursor / Windsurf", color: "text-zinc-500" },
                { label: "Agents (Action)", value: "Claude Code", color: "text-zinc-500" },
                { label: "Registry (Record)", value: "Sidelith", color: "text-blue-400 font-bold" }
              ].map((item, i) => (
                <div key={i} className="px-6 py-4 rounded-2xl bg-white/5 border border-white/10 flex flex-col items-center">
                  <span className="text-[10px] uppercase tracking-widest text-zinc-600 mb-1">{item.label}</span>
                  <span className={item.color}>{item.value}</span>
                </div>
              ))}
            </div>

            {/* Honest Comparison */}
            <div className="overflow-x-auto mb-16 rounded-3xl border border-white/10 bg-zinc-900/30 p-1">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="py-4 px-6 text-zinc-400 font-medium tracking-wide text-sm uppercase">Capability</th>
                    <th className="py-4 px-6 text-center">
                      <span className="text-emerald-400 font-bold tracking-tight">The Sovereign Brain</span>
                    </th>
                    <th className="py-4 px-6 text-center font-medium">Standard LLMs / IDEs</th>
                  </tr>
                </thead>
                <tbody className="text-base text-sm">
                  <tr
                    onClick={() => setActiveFeature("The Strategic Registry")}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors bg-white/[0.02] cursor-pointer group"
                  >
                    <td className="py-4 px-6 group-hover:pl-8 transition-all duration-300">
                      <div className="flex items-center gap-2">
                        <div>
                          <p className="font-medium text-white group-hover:text-emerald-400 transition-colors flex items-center gap-2">
                            The Sovereign Vault <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                          </p>
                          <p className="text-sm text-zinc-500">Immutable Strategic Registry</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center gap-1.5 text-green-400 font-medium bg-green-500/10 px-3 py-1 rounded-full border border-green-500/20"><Check className="w-4 h-4" /> Lifetime Context</span>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center gap-1.5 text-zinc-500 font-medium px-3 py-1 bg-zinc-800/50 rounded-full border border-white/5">Session Only</span>
                    </td>
                  </tr>
                  <tr
                    onClick={() => setActiveFeature("Context-Engine (RLM)")}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer group"
                  >
                    <td className="py-4 px-6 group-hover:pl-8 transition-all duration-300">
                      <p className="font-medium text-white group-hover:text-blue-400 transition-colors flex items-center gap-2">
                        Context-Engine (RLM) <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </p>
                      <p className="text-sm text-zinc-500">Eliminates "Context Rot"</p>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center justify-center gap-2 text-green-400 text-sm font-medium"><Check className="w-4 h-4" /> Recursive Reasoner</span>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center justify-center gap-2 text-yellow-500 text-sm font-medium opacity-80">Flat Search (RAG)</span>
                    </td>
                  </tr>
                  <tr
                    onClick={() => setActiveFeature("Neural Logic Graph")}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer group"
                  >
                    <td className="py-4 px-6 group-hover:pl-8 transition-all duration-300">
                      <p className="font-medium text-white group-hover:text-blue-400 transition-colors flex items-center gap-2">
                        Neural Logic Graph <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </p>
                      <p className="text-sm text-zinc-500">Multi-Pass Tree-Sitter Analysis</p>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-green-500/10 text-green-400 border border-green-500/20 mx-auto"><Check className="w-4 h-4" /></span>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center gap-1.5 text-yellow-500 font-medium bg-yellow-500/10 px-3 py-1 rounded-full border border-yellow-500/20"><AlertCircle className="w-4 h-4" /> Partial</span>
                    </td>
                  </tr>
                  <tr
                    onClick={() => setActiveFeature("Architectural Forensics")}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer group"
                  >
                    <td className="py-4 px-6 group-hover:pl-8 transition-all duration-300">
                      <p className="font-medium text-white group-hover:text-blue-400 transition-colors flex items-center gap-2">
                        Architectural Forensics <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </p>
                      <p className="text-sm text-zinc-500">Detect Logic Drift instantly</p>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-green-500/10 text-green-400 border border-green-500/20 mx-auto"><Check className="w-4 h-4" /></span>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-red-500/10 text-red-400 border border-red-500/20 mx-auto"><X className="w-4 h-4" /></span>
                    </td>
                  </tr>
                  <tr
                    onClick={() => setActiveFeature("Virtual User Testing")}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer group"
                  >
                    <td className="py-4 px-6 group-hover:pl-8 transition-all duration-300">
                      <p className="font-medium text-white group-hover:text-blue-400 transition-colors flex items-center gap-2">
                        Virtual User Testing <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </p>
                      <p className="text-sm text-zinc-500">Simulate specialized personas</p>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-green-500/10 text-green-400 border border-green-500/20 mx-auto"><Check className="w-4 h-4" /></span>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center gap-1 text-zinc-500"><X className="w-4 h-4" /></span>
                    </td>
                  </tr>
                  <tr>
                    <td className="py-4 px-6">
                      <p className="font-medium text-white">Writes Code</p>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center gap-1 text-zinc-500"><X className="w-4 h-4" /> No (We guide, you code)</span>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center gap-1 text-green-400 font-medium"><Check className="w-4 h-4" /> World Class</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* Feature Specs Detail View */}
            <div className={`fixed inset-y-0 right-0 w-full md:w-[480px] bg-black/90 backdrop-blur-xl border-l border-white/10 p-8 transform transition-transform duration-500 ease-out z-50 ${activeFeature ? 'translate-x-0' : 'translate-x-full'}`}>
              <button
                onClick={() => setActiveFeature(null)}
                className="absolute top-6 right-6 p-2 rounded-full hover:bg-white/10 text-zinc-400 hover:text-white transition-colors"
              >
                <X className="w-6 h-6" />
              </button>

              {activeFeature && CAPABILITY_SPECS[activeFeature] && (
                <div className="h-full flex flex-col animate-in fade-in slide-in-from-right-4 duration-500">
                  <div className="mb-8 overflow-hidden">
                    <div className="text-xs font-mono text-blue-400 mb-2 uppercase tracking-widest">System Capability</div>
                    <h3 className="text-3xl font-bold text-white mb-4">{activeFeature}</h3>
                    <p className="text-zinc-400 leading-relaxed text-lg">{CAPABILITY_SPECS[activeFeature].description}</p>
                  </div>

                  <div className="flex-1 overflow-y-auto pr-2">
                    <div className="space-y-6">
                      <div className="bg-white/5 rounded-2xl p-6 border border-white/5">
                        <div className="text-sm font-medium text-white mb-4 flex items-center gap-2">
                          <Terminal className="w-4 h-4 text-purple-400" /> Technical Specs
                        </div>
                        <div className="space-y-3">
                          {CAPABILITY_SPECS[activeFeature].specs.map((spec: any, i: number) => (
                            <div key={i} className="flex justify-between items-center py-2 border-b border-white/5 last:border-0">
                              <span className="text-zinc-500 text-sm font-mono">{spec.label}</span>
                              <span className="text-white text-sm font-medium text-right">{spec.value}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/5 rounded-2xl p-6 border border-blue-500/20">
                        <div className="text-sm font-medium text-blue-300 mb-4 flex items-center gap-2">
                          <Zap className="w-4 h-4" /> Strategic Moat
                        </div>
                        <div className="space-y-3">
                          {CAPABILITY_SPECS[activeFeature].moat.split('\n').map((line, i) => (
                            <p key={i} className="text-sm text-blue-100/80 leading-relaxed flex items-start gap-2">
                              {line}
                            </p>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Backdrop for slider */}
            {activeFeature && (
              <div
                className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity duration-500 animate-in fade-in"
                onClick={() => setActiveFeature(null)}
              />
            )}

            {/* The Point */}
            <div className="text-center max-w-2xl mx-auto p-8 rounded-3xl border border-white/10 bg-zinc-900/30 hover:border-white/20 transition-colors">
              <p className="text-xl text-white mb-6 font-bold uppercase tracking-tighter italic">
                The Sovereign Engineering Stack
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div className="p-3 bg-white/5 rounded-xl border border-white/5">
                  <p className="text-white font-bold text-sm">IDE</p>
                  <p className="text-zinc-500 text-xs">Cursor</p>
                </div>
                <div className="p-3 bg-white/5 rounded-xl border border-white/5">
                  <p className="text-white font-bold text-sm">Execution</p>
                  <p className="text-zinc-500 text-xs">Claude Code</p>
                </div>
                <div className="p-3 bg-blue-500/10 rounded-xl border border-blue-500/20">
                  <p className="text-blue-400 font-bold text-sm">Registry</p>
                  <p className="text-blue-500 text-xs">Sidelith</p>
                </div>
              </div>
              <p className="text-xs text-zinc-600 border-t border-white/5 pt-4 italic">
                * Sidelith maintains the forward-looking <strong>Decision Graph</strong> required for mission-critical architecture.
              </p>
            </div>
          </div>
        </section>

        {/* The Why & How (Core Values) */}
        <section className="py-32 px-6 bg-zinc-900/40 border-y border-white/5 relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(59,130,246,0.05),transparent)] pointer-events-none" />
          <div className="max-w-6xl mx-auto relative z-10">
            <div className="text-center mb-24">
              <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-4 uppercase italic">The Core Values</h2>
              <p className="text-zinc-400 max-w-2xl mx-auto uppercase tracking-widest text-[10px] font-black">Architecture is a trajectory, not a snapshot.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-16">
              <div className="space-y-4">
                <div className="h-1 w-12 bg-blue-500 mb-6" />
                <h3 className="text-2xl font-black uppercase italic tracking-tight">Stop Erosion</h3>
                <p className="text-zinc-400 leading-relaxed text-sm max-w-[280px]">
                  When you close your IDE, architectural intent evaporates. Sidelith captures the <strong>&quot;Invisible Why&quot;</strong> before it drains into debt.
                </p>
                <p className="text-[9px] text-blue-400 font-bold uppercase tracking-widest">Leverage: HIGH</p>
              </div>

              <div className="space-y-4">
                <div className="h-1 w-12 bg-purple-500 mb-6" />
                <h3 className="text-2xl font-black uppercase italic tracking-tight">System of Record</h3>
                <p className="text-zinc-400 leading-relaxed text-sm max-w-[280px]">
                  Editors manage text. Agents manage action. Sidelith manages <strong>Truth</strong>—the ground-truth required for autonomous engineering.
                </p>
                <p className="text-[9px] text-purple-400 font-bold uppercase tracking-widest">Registry: IMMUTABLE</p>
              </div>

              <div className="space-y-4">
                <div className="h-1 w-12 bg-green-500 mb-6" />
                <h3 className="text-2xl font-black uppercase italic tracking-tight">Sovereign Intel</h3>
                <p className="text-zinc-400 leading-relaxed text-sm max-w-[280px]">
                  Optimized performance without privacy loss. Reach <strong>400st IQ</strong> with zero PII egress via Judicial Scrubbing.
                </p>
                <p className="text-[9px] text-green-400 font-bold uppercase tracking-widest">Latency: 110ms</p>
              </div>
            </div>
          </div>
        </section>

        {/* The Storytelling Bridge: The Invisible Why */}
        <section className="py-32 px-6 relative overflow-hidden">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl md:text-5xl font-black tracking-tighter mb-12 uppercase italic leading-tight">
              Forgotten Context <br /> kills projects.
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-left max-w-3xl mx-auto">
              <div className="p-8 rounded-3xl bg-zinc-900/30 border border-white/5 space-y-4">
                <p className="text-sm text-zinc-500 font-bold uppercase tracking-widest">Normal Development</p>
                <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
                  <div className="h-full bg-red-500 w-[70%]" />
                </div>
                <p className="text-zinc-400 text-xs italic leading-relaxed">
                  &quot;We built this auth layer using custom JWTs. 6 months later, nobody remembers why. We refactor, break it, and lose 2 weeks.&quot;
                </p>
              </div>
              <div className="p-8 rounded-3xl bg-blue-500/5 border border-blue-500/10 space-y-4">
                <p className="text-sm text-blue-400 font-bold uppercase tracking-widest">Sidelith Powered</p>
                <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 w-full" />
                </div>
                <p className="text-zinc-300 text-xs font-medium leading-relaxed">
                  &quot;Hey Side, why custom JWTs?&quot; — Side recalls the decision log instantly, saves the refactor, and keeps the project on trajectory.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* The Silent Observer - Passive Strategy */}
        <section className="py-24 px-6 bg-black relative overflow-hidden">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-blue-500/50 to-transparent" />
          <div className="max-w-5xl mx-auto">
            <div className="flex flex-col md:flex-row items-center gap-16">
              <div className="flex-1 space-y-6">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-blue-500/20 bg-blue-500/10 text-[10px] text-blue-400 font-black uppercase tracking-widest">
                  Zero Distraction Engine
                </div>
                <h2 className="text-4xl md:text-5xl font-black tracking-tighter uppercase italic leading-tight">
                  The Silent <br />Observer.
                </h2>
                <p className="text-xl text-zinc-300 leading-relaxed font-medium">
                  Sidelith doesn&apos;t ask for your attention. It earns its place by listening to your architectural transitions and measuring <strong>Human Leverage</strong> in the background.
                </p>
                <div className="space-y-4 pt-4 text-zinc-400">
                  <div className="flex gap-4">
                    <div className="w-1 h-1 rounded-full bg-blue-500 mt-2" />
                    <p className="text-sm"><strong>Passive Instrumentation</strong>: Automatically logs outcomes and calculates leverage (Outcome/Action) without a single popup.</p>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-1 h-1 rounded-full bg-blue-500 mt-2" />
                    <p className="text-sm"><strong>Zero-Latency Local Sync</strong>: Your IDE stays fast. Sidelith operates strictly on a parallel thread with local-first persistence.</p>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-1 h-1 rounded-full bg-blue-500 mt-2" />
                    <p className="text-sm"><strong>Habitual Feedback</strong>: A silent coach that evolves your MONOLITH.md, turning architectural awareness into a second-nature instinct.</p>
                  </div>
                </div>
              </div>

              <div className="flex-1 w-full max-w-md p-8 rounded-3xl bg-zinc-900/50 border border-white/5 relative group transition-all duration-500 hover:border-blue-500/20">
                <div className="absolute inset-0 bg-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-3xl" />
                <div className="relative z-10 space-y-6">
                  <div className="flex justify-between items-center pb-4 border-b border-white/5">
                    <span className="text-[10px] font-black uppercase tracking-widest text-[#a1a1a1]">Active Instrumentation</span>
                    <span className="text-[10px] text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 uppercase tracking-tighter">Forensic Thread: T3_SYNC</span>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between text-[11px]">
                      <span className="text-zinc-500 uppercase font-black">Leverage Index</span>
                      <span className="text-white font-black italic">2.44x [OUTCOME/ACTION]</span>
                    </div>
                    <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 w-[60%]" />
                    </div>
                  </div>
                  <div className="pt-4 space-y-3 border-t border-white/5">
                    <p className="text-[10px] font-black uppercase tracking-widest text-zinc-500 mb-1">Contextual Integrity</p>
                    <div className="space-y-2">
                      <div className="text-[10px] text-zinc-300 flex items-center justify-between">
                        <span>Logic Chain Stability</span>
                        <span className="text-emerald-400 font-bold">98.2%</span>
                      </div>
                      <div className="text-[10px] text-zinc-300 flex items-center justify-between">
                        <span>Drift Neutralization</span>
                        <span className="text-blue-400 font-bold">ACTIVE</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Case Logs - Forensic Evidence */}
        <section id="caselogs" className="py-20 px-6 border-t border-white/5">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-4xl font-black tracking-tighter text-center mb-4 uppercase italic">Forensic Evidence</h2>
            <p className="text-zinc-400 text-center mb-16 uppercase tracking-widest text-[10px] font-black">When Side saves you from a 2-week mistake, it pays for itself forever.</p>

            <div className="bg-zinc-900/30 rounded-3xl border border-white/10 overflow-hidden">
              <div className="grid grid-cols-1 md:grid-cols-12 min-h-[500px]">
                {/* Left: Tabs */}
                <div className="md:col-span-4 border-r border-white/10 bg-black/20">
                  <div className="p-4 space-y-2">
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
                        className={`w-full text-left px-4 py-4 rounded-xl transition-all duration-200 flex items-center justify-between border ${activeCase === tab.id
                          ? "bg-white/10 border-white/10 text-white shadow-lg"
                          : "border-transparent text-zinc-500 hover:text-zinc-300 hover:bg-white/5"
                          }`}
                      >
                        <div className="flex items-center gap-3">
                          <tab.icon className={`w-4 h-4 ${activeCase === tab.id ? "text-white" : "text-zinc-600"}`} />
                          <span className="font-bold text-xs uppercase tracking-tighter italic">{tab.label}</span>
                        </div>
                        <span className={`text-[9px] font-black px-1.5 py-0.5 rounded border uppercase italic tracking-widest ${activeCase === tab.id
                          ? "bg-emerald-500 text-black border-emerald-500"
                          : "bg-zinc-800 border-zinc-700 opacity-30"
                          }`}>
                          {tab.save}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Right: Visual */}
                <div className="md:col-span-8 bg-black/50 p-6 md:p-8 flex flex-col relative">
                  {/* Decorative Background */}
                  <div className="absolute top-0 right-0 w-full h-full bg-gradient-to-br from-purple-500/5 via-blue-500/5 to-transparent pointer-events-none" />

                  {/* Header */}
                  <div className="flex items-center justify-between mb-8 relative z-10">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full animate-pulse ${activeCase === 'auth' ? 'bg-red-500' :
                        activeCase === 'research' ? 'bg-cyan-500' :
                          activeCase === 'fork' ? 'bg-blue-500' :
                            activeCase === 'pivot' ? 'bg-purple-500' :
                              activeCase === 'scale' ? 'bg-yellow-500' : 'bg-red-500'
                        }`} />
                      <span className="text-xs font-mono text-zinc-500 uppercase tracking-widest">Live Intervention</span>
                    </div>
                    {activeCase === 'auth' && <span className="text-xs font-bold text-red-500 bg-red-500/10 px-2 py-1 rounded border border-red-500/20">CRITICAL SAVE</span>}
                    {activeCase === 'research' && <span className="text-xs font-bold text-cyan-400 bg-cyan-500/10 px-2 py-1 rounded border border-cyan-500/20">MARKET INTEL</span>}
                    {activeCase === 'fork' && <span className="text-xs font-bold text-blue-400 bg-blue-500/10 px-2 py-1 rounded border border-blue-500/20">OPTIMIZATION</span>}
                    {activeCase === 'pivot' && <span className="text-xs font-bold text-purple-400 bg-purple-500/10 px-2 py-1 rounded border border-purple-500/20">STRATEGY ALIGNMENT</span>}
                    {activeCase === 'scale' && <span className="text-xs font-bold text-yellow-400 bg-yellow-500/10 px-2 py-1 rounded border border-yellow-500/20">COST SAVINGS</span>}
                    {activeCase === 'sec' && <span className="text-xs font-bold text-orange-400 bg-orange-500/10 px-2 py-1 rounded border border-orange-500/20">SECURITY RISK</span>}
                  </div>

                  {/* Chat Content */}
                  <div className="flex-grow space-y-6 relative z-10">
                    {/* User Message */}
                    <div className="flex justify-end">
                      <div className="bg-blue-600 text-white px-5 py-4 rounded-2xl rounded-br-none text-sm max-w-[85%] shadow-lg shadow-blue-900/20 font-medium">
                        {activeCase === 'auth' && "Logic thread Jan14 flagged for hydration drift. Recommend flattening isomorphic state?"}
                        {activeCase === 'research' && "LLM Cost Forecast: Reasoning threads on 70B are yielding <30% accuracy. Switch to 405B?"}
                        {activeCase === 'fork' && "Multi-pass analysis stalling at depth 4 in Rust macros. Request deep recursive scan?"}
                        {activeCase === 'pivot' && "Strategy Audit: SOC2 Type 2 compliance requires Judicial integrity in log sinks."}
                        {activeCase === 'scale' && "Forensic TTFT Alert: Cold starts in Server Actions hitting 1.2s. Optimization path?"}
                        {activeCase === 'sec' && "Registry Scan: Found raw PII in webhook debug logs. Enable forensic masking?"}
                      </div>
                    </div>

                    {/* CSO Message */}
                    <div className="flex justify-start">
                      <div className="bg-zinc-800 border border-white/10 px-6 py-5 rounded-2xl rounded-bl-none max-w-[95%] shadow-xl">
                        <div className="font-mono text-sm leading-relaxed">
                          {/* AUTH / HYDRATION CONTENT */}
                          {activeCase === 'auth' && <>
                            <p className="text-emerald-400 font-black mb-3 flex items-center gap-2"><Shield className="w-4 h-4" /> ⬛ FORENSIC RESOLUTION</p>
                            <p className="text-white mb-3">Hydration mismatch detected in `logic_thread_09`. The Server Action `getProfile()` is returning a stale HMR cache during SSR.</p>
                            <div className="bg-black/30 p-3 rounded border border-white/5 mb-3">
                              <p className="text-zinc-500 text-[10px] uppercase font-black mb-1 tracking-widest">Trajectory Correction:</p>
                              <code className="text-[11px] text-emerald-300">{`export const dynamic = 'force-dynamic';\n// Drift resolved by flattening isomorphic state.`}</code>
                            </div>
                            <p className="text-zinc-500 text-[10px] uppercase font-black tracking-widest pl-3 border-l-2 border-emerald-500/20">
                              Strategic IQ: +12 points (Architecture debt cleared)
                            </p>
                          </>}

                          {/* COST FORENSICS CONTENT */}
                          {activeCase === 'research' && <>
                            <p className="text-cyan-400 font-black mb-3 flex items-center gap-2"><Globe className="w-4 h-4" /> 📡 SYSTEM CAPACITY AUDIT</p>
                            <p className="text-white mb-3">Directing LLM traffic to Groq 405B for this logic thread. Reasoning: 70B fails the recursive intent test for multi-pass AST analysis.</p>
                            <div className="bg-cyan-500/10 border border-cyan-500/20 p-4 rounded mb-3">
                              <p className="text-cyan-300 text-[10px] font-black mb-2 uppercase tracking-widest">LEVERAGE OPTIMIZATION:</p>
                              <div className="space-y-1.5">
                                <div className="flex justify-between text-[11px]">
                                  <span className="text-white">Outcome Yield</span>
                                  <span className="text-green-400 font-bold">▲ +440% (Forensic Accuracy)</span>
                                </div>
                                <div className="flex justify-between text-[11px]">
                                  <span className="text-zinc-400">Monthly SUs</span>
                                  <span className="text-red-400">▼ Normalized via pruning</span>
                                </div>
                              </div>
                            </div>
                            <p className="text-zinc-400 text-[10px] font-black uppercase tracking-widest underline decoration-cyan-500/20 underline-offset-4">
                              Manual Override: Use local Llama 3.1 8B for non-strategic pruning.
                            </p>
                          </>}

                          {/* RECURSIVE MACROS CONTENT */}
                          {activeCase === 'fork' && <>
                            <p className="text-blue-400 font-black mb-3 flex items-center gap-2"><Brain className="w-4 h-4" /> 💡 MULTI-PASS TREE-SITTER</p>
                            <p className="text-white mb-3">Detected safe recursion depth reached in Rust macro expansion. Trajectory drift flagged.</p>
                            <div className="grid grid-cols-1 gap-3 mb-3">
                              <div className="bg-white/5 border border-white/10 p-4 rounded">
                                <p className="text-zinc-500 text-[10px] font-black mb-1 uppercase tracking-widest">Logical Inconsistency:</p>
                                <p className="text-white text-xs leading-relaxed italic">The expansion of `#[derive(Forensics)]` introduces a circular logic thread at depth 4. AST precision requires flattening.</p>
                              </div>
                            </div>
                            <p className="text-zinc-500 text-[10px] font-black uppercase tracking-widest">
                              Registry Update: Immutable node added to forensic graph.
                            </p>
                          </>}

                          {/* SOC2 CONTENT */}
                          {activeCase === 'pivot' && <>
                            <p className="text-purple-400 font-black mb-3 flex items-center gap-2"><FileText className="w-4 h-4" /> 🛑 COMPLIANCE PIVOT</p>
                            <p className="text-white mb-2">Switching to **SOC2 Type 2 Governance**. Implementation of `audit_sink` must follow the Judicial Integrity protocol.</p>
                            <div className="bg-purple-500/10 border border-purple-500/20 p-4 rounded mb-3">
                              <p className="text-purple-300 text-[10px] font-black uppercase tracking-widest mb-1">Audit Directive:</p>
                              <div className="text-[11px] text-zinc-300 leading-relaxed italic">
                                &quot;PII from customer sessions is currently flowing into local logs. This violates the 'Sealed Registry' constraint for Enterprise Tier.&quot;
                              </div>
                            </div>
                            <p className="text-emerald-400 font-black mt-2 text-[10px] flex items-center gap-1 uppercase tracking-widest underline underline-offset-4">
                              <Check className="w-3 h-3" /> Fix Applied: Judicial Scrubbing enabled for all log sinks.
                            </p>
                          </>}

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
        </section>

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
        </section>

        {/* The Habit Loop Section */}
        <section className="py-24 px-6 bg-black relative">
          <div className="max-w-6xl mx-auto">
            <div className="flex flex-col md:flex-row-reverse items-center gap-16">
              <div className="flex-1 space-y-6">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-purple-500/20 bg-purple-500/10 text-[10px] text-purple-400 font-black uppercase tracking-widest italic">
                  Daily Strategic Anchor
                </div>
                <h2 className="text-4xl md:text-5xl font-black tracking-tighter uppercase italic leading-tight">
                  The Monolith <br /> Habit.
                </h2>
                <p className="text-xl text-zinc-300 leading-relaxed font-medium">
                  Sustainable engineering requires a single source of truth. Sidelith maintains an immutable <code>.side/MONOLITH.md</code> dashboard that becomes your project&apos;s silent CTO.
                </p>
                <div className="space-y-6 pt-4 text-zinc-400">
                  <div className="flex gap-4">
                    <div className="w-1.5 h-1.5 rounded-full bg-purple-500 mt-2 flex-shrink-0" />
                    <div>
                      <p className="text-sm text-white font-bold uppercase tracking-widest text-xs mb-1">Sealed Registry</p>
                      <p className="text-sm">Automatically hardened to read-only. A trusted, tamper-proof record of architectural logic.</p>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-1.5 h-1.5 rounded-full bg-purple-500 mt-2 flex-shrink-0" />
                    <div>
                      <p className="text-sm text-white font-bold uppercase tracking-widest text-xs mb-1">Provocation Engine</p>
                      <p className="text-sm">Doesn&apos;t just show stats; it challenges your trajectory with forensic insights.</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex-1 w-full p-2 rounded-3xl bg-zinc-900/50 border border-white/5 shadow-2xl">
                <div className="bg-black rounded-2xl overflow-hidden font-mono text-[10px] text-zinc-500 p-8 border border-white/5">
                  <div className="space-y-6">
                    <div className="flex justify-between items-end border-b border-white/5 pb-2">
                      <div>
                        <p className="text-white font-black text-sm uppercase italic tracking-tighter"># PRIME_REGISTRY</p>
                        <p className="text-zinc-500 uppercase tracking-widest text-[8px]">Session ID: <span className="text-zinc-400 font-mono">T3_HYDRATION_FIX</span></p>
                      </div>
                      <p className="text-emerald-400 font-black text-[10px] italic">IQ: 362/400</p>
                    </div>
                    <div className="space-y-4 pt-2">
                      <div className="space-y-1.5 font-mono">
                        <p className="text-zinc-500 uppercase tracking-widest text-[9px]">Trajectory Insight</p>
                        <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden">
                          <div className="h-full bg-emerald-500 w-[91%]" />
                        </div>
                      </div>
                      <div className="p-3 bg-blue-500/5 border border-blue-500/10 rounded-sm">
                        <p className="text-blue-400 text-[10px] font-black uppercase mb-1 tracking-tighter italic">Fix Drift: T3</p>
                        <p className="text-zinc-400 leading-relaxed text-[10px]">Registry updated. Hydration mismatch resolved in isomorphic state sync. ROI: 4.2h saved.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* The Sovereign Moats - Technical Depth */}
        <section className="py-24 px-6 bg-zinc-900/20 border-t border-white/5">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-20">
              <h2 className="text-5xl md:text-6xl font-black tracking-tighter mb-4 uppercase italic font-heading">Sovereign Moats.</h2>
              <p className="text-zinc-500 max-w-2xl mx-auto uppercase tracking-[0.4em] text-[10px] font-black">Engineering excellence is the only marketing strategy.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* Moat 1 */}
              <div className="p-8 rounded-3xl bg-black border border-white/5 hover:border-blue-500/20 transition-colors group">
                <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <Terminal className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-xl font-black text-white mb-3 uppercase italic tracking-tighter">Multi-Pass Tree-Sitter</h3>
                <p className="text-sm text-zinc-400 leading-relaxed mb-6">
                  While basic RAG tools guess, Sidelith performantly builds a full <strong>Abstract Syntax Tree</strong> of your project, mapping every import, side-effect, and logical dependency.
                </p>
                <div className="bg-zinc-900/50 rounded-lg p-3 border border-white/5 font-mono text-[9px] space-y-1">
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Parsing Depth</span>
                    <span className="text-emerald-400">∞ (Recursive)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Cross-Language Docs</span>
                    <span className="text-white">Isomorphic</span>
                  </div>
                </div>
              </div>

              {/* Moat 2 */}
              <div className="p-8 rounded-3xl bg-black border border-white/5 hover:border-purple-500/20 transition-colors group">
                <div className="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <Brain className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="text-xl font-black text-white mb-3 uppercase italic tracking-tighter">Provocation Engine</h3>
                <p className="text-sm text-zinc-400 leading-relaxed mb-6">
                  Our proprietary Strategist doesn&apos;t just answer questions—it <strong>provokes</strong>. It challenges you when implementation complexity exceeds strategic budgets.
                </p>
                <div className="bg-purple-500/5 rounded-lg p-3 border border-purple-500/10 font-mono text-[9px] space-y-1">
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Strategic IQ Scale</span>
                    <span className="text-purple-400">400_PT_FORENSIC</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Provocation Rate</span>
                    <span className="text-white">Context-Adaptive</span>
                  </div>
                </div>
              </div>

              {/* Moat 3 */}
              <div className="p-8 rounded-3xl bg-black border border-white/5 hover:border-green-500/20 transition-colors group">
                <div className="w-12 h-12 rounded-2xl bg-green-500/10 border border-green-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <Shield className="w-6 h-6 text-green-400" />
                </div>
                <h3 className="text-xl font-black text-white mb-3 uppercase italic tracking-tighter">Judicial Integrity</h3>
                <p className="text-sm text-zinc-400 leading-relaxed mb-6">
                  Sovereignty means control. Our **Judicial Scrubbing** protocol forensically removes PII and sensitive tokens locally before any sanitized metadata is ever synced.
                </p>
                <div className="bg-green-500/5 rounded-lg p-3 border border-green-500/10 font-mono text-[9px] space-y-1">
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Encryption Layer</span>
                    <span className="text-emerald-400">AES-256 (Local)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Egress Integrity</span>
                    <span className="text-white">100% Sanitized</span>
                  </div>
                </div>
              </div>

              {/* Moat 4 */}
              <div className="p-8 rounded-3xl bg-black border border-white/5 hover:border-orange-500/20 transition-colors group">
                <div className="w-12 h-12 rounded-2xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <RefreshCw className="w-6 h-6 text-orange-400" />
                </div>
                <h3 className="text-xl font-black text-white mb-3 uppercase italic tracking-tighter">Local-First Architecture</h3>
                <p className="text-sm text-zinc-400 leading-relaxed mb-6">
                  Sidelith operates on your hardware. Zero dependency on cloud latency. Your Registry is available offline, secured by SQLite encryption.
                </p>
                <div className="bg-orange-500/5 rounded-lg p-3 border border-orange-500/10 font-mono text-[9px] space-y-1">
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Storage Kernel</span>
                    <span className="text-orange-400">SQLite (Encrypted)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Cloud Dependency</span>
                    <span className="text-white">Zero (Local Core)</span>
                  </div>
                </div>
              </div>

              {/* Moat 5 */}
              <div className="p-8 rounded-3xl bg-black border border-white/5 hover:border-cyan-500/20 transition-colors group">
                <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <Zap className="w-6 h-6 text-cyan-400" />
                </div>
                <h3 className="text-xl font-black text-white mb-3 uppercase italic tracking-tighter">Human Leverage Engine</h3>
                <p className="text-sm text-zinc-400 leading-relaxed mb-6">
                  By measuring <strong>Outcome / Action</strong> indices, Sidelith provides a quantitative mirror of your effectiveness as a senior engineer.
                </p>
                <div className="bg-cyan-500/5 rounded-lg p-3 border border-cyan-500/10 font-mono text-[9px] space-y-1">
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Leverage Unit</span>
                    <span className="text-cyan-400">hL (Outcome/Action)</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Tracking Mode</span>
                    <span className="text-white">Passive Passive</span>
                  </div>
                </div>
              </div>

              {/* Moat 6 */}
              <div className="p-8 rounded-3xl bg-black border border-white/5 hover:border-zinc-500/20 transition-colors group">
                <div className="w-12 h-12 rounded-2xl bg-white/10 border border-white/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-black text-white mb-3 uppercase italic tracking-tighter">Sovereign Registry</h3>
                <p className="text-sm text-zinc-400 leading-relaxed mb-6">
                  Turn transient chat bubbles and commit messages into a <strong>Persistent Logical Asset</strong> that adds real value to project valuation.
                </p>
                <div className="bg-zinc-500/10 rounded-lg p-3 border border-white/5 font-mono text-[9px] space-y-1">
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Asset Type</span>
                    <span className="text-white">Logical Registry</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Data Standard</span>
                    <span className="text-zinc-400">Open-Forensic</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Install Section */}
        <section id="install" className="py-20 px-6 bg-black">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-4 uppercase italic tracking-tighter">Add to your IDE in 2 minutes</h2>
            <p className="text-zinc-400 text-center mb-12 uppercase tracking-widest text-[10px] font-black opacity-60">Works alongside Cursor, Windsurf, Claude Desktop.</p>

            <div className="space-y-4">
              <div className="rounded-xl border border-white/5 bg-[#0c0c0e] p-6 group hover:border-emerald-500/20 transition-colors">
                <div className="flex items-center gap-4 mb-4">
                  <span className="w-8 h-8 rounded-lg bg-white text-black font-black flex items-center justify-center text-xs">01</span>
                  <span className="font-black uppercase italic tracking-tighter text-white">Initialize Kernel</span>
                </div>
                <div className="bg-black rounded-lg p-5 font-mono flex items-center justify-between border border-white/10 group-hover:border-white/20">
                  <code className="text-emerald-400 text-base">pip install sidelith</code>
                  <button className="text-zinc-500 hover:text-white transition-colors" onClick={handleCopy}><Copy className="w-4 h-4" /></button>
                </div>
              </div>

              <div className="rounded-xl border border-white/5 bg-[#0c0c0e] p-6">
                <div className="flex items-center gap-4 mb-4">
                  <span className="w-8 h-8 rounded-lg bg-white text-black font-black flex items-center justify-center text-xs">02</span>
                  <span className="font-black uppercase italic tracking-tighter text-white">Hydrate MCP Context</span>
                </div>
                <div className="bg-black rounded-lg p-5 font-mono text-sm overflow-x-auto border border-white/10">
                  <pre className="text-zinc-500 leading-relaxed">{`{
  "mcpServers": {
    "sidelith": {
      "command": "python",
      "args": ["-m", "side.server"]
    }
  }
}`}</pre>
                </div>
              </div>

              <div className="rounded-xl border border-white/5 bg-[#0c0c0e] p-6">
                <div className="flex items-center gap-4 mb-4">
                  <span className="w-8 h-8 rounded-lg bg-white text-black font-black flex items-center justify-center text-xs">03</span>
                  <span className="font-black uppercase italic tracking-tighter text-white">Execute Forensic Audit</span>
                </div>
                <div className="bg-black rounded-lg p-5 font-mono border border-white/10">
                  <code className="text-blue-400 text-base italic">&quot;Hey Side, show me the architectural drift in thread T3.&quot;</code>
                </div>
              </div>
            </div>

            <div className="mt-10 text-center">
              <Link href="/login" className="h-16 px-12 rounded-full bg-white text-black font-black hover:bg-zinc-200 transition-all inline-flex items-center gap-2 text-xl uppercase italic tracking-tighter shadow-2xl">
                Claim Your Registry <ChevronRight className="w-6 h-6" />
              </Link>
              <p className="text-zinc-500 text-sm mt-4 font-medium italic">Join the Sovereign Layer. No credit card required.</p>
            </div>
          </div>
        </section>

        {/* Trust */}
        < section className="py-16 px-6 border-t border-white/10" >
          <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <p className="text-3xl font-black text-white mb-1">100%</p>
              <p className="text-zinc-400 font-bold uppercase tracking-tighter text-[10px]">Judicial Sync</p>
            </div>
            <div>
              <p className="text-3xl font-black text-white mb-1">&lt;110ms</p>
              <p className="text-zinc-400 font-bold uppercase tracking-tighter text-[10px]">TTFT (Groq 70B)</p>
            </div>
            <div>
              <p className="text-3xl font-black text-white mb-1">LOCAL</p>
              <p className="text-zinc-400 font-bold uppercase tracking-tighter text-[10px]">First Architecture</p>
            </div>
            <div>
              <p className="text-3xl font-black text-white mb-1">MIT</p>
              <p className="text-zinc-400 font-bold uppercase tracking-tighter text-[10px]">Open Standards</p>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-white/10 py-10 px-6">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start gap-8">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <div className="h-5 w-5 bg-white rounded-sm" />
                <span className="font-black text-xl tracking-tighter uppercase italic text-white">Sidelith</span>
              </div>
              <p className="text-zinc-400 text-sm font-medium leading-relaxed">The System of Record for Project Context. <br />Professional-grade project trajectory management.</p>
            </div>
            <div className="flex gap-12 text-sm text-zinc-300 font-medium">
              <div className="flex flex-col gap-2">
                <Link href="#forensics" className="hover:text-white transition-colors">Forensics & Strategy</Link>
                <Link href="#caselogs" className="hover:text-white transition-colors">Case Logs</Link>
                <Link href="#install" className="hover:text-white transition-colors">Install</Link>
                <Link href="/pricing" className="hover:text-white transition-colors">Infrastructure</Link>
              </div>
              <div className="flex flex-col gap-2">
                <Link href="https://github.com/erhan-github/side" className="hover:text-white transition-colors">GitHub</Link>
                <Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link>
                <Link href="/terms" className="hover:text-white transition-colors">Terms</Link>
              </div>
            </div>
          </div>
        </footer>

      </main>
    </div>
  );
}
