"use client";

import { Terminal, ChevronRight, Zap, Copy, Brain, Shield, Users, Eye, FileText, Check, X, AlertCircle, GitBranch, RefreshCw, AlertTriangle, ChevronDown, Globe } from "lucide-react";
import Link from "next/link";
import { useState, useEffect } from "react";

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
  "Deep Logic Graph": {
    description: "We don't guess with regex. We parse the actual Abstract Syntax Tree (AST) to build a pixel-perfect map of your code's logic flow. We know exactly which class imports which module, and where every function is defined.",
    specs: [
      { label: "Parser Engine", value: "Native Python AST (ast module)" },
      { label: "Graph Topology", value: "Directed Acyclic Graph (DAG)" },
      { label: "Node Types", value: "Classes, Functions, Imports, Mixins" },
      { label: "Analysis Latency", value: "< 200ms per file" }
    ],
    moat: "While typical AI tools just read your code as 'text', sideMCP understands it as 'structure'. This allows us to detect architectural drift and circular dependencies instantly."
  },
  "Strategic Roadmap (plan.md)": {
    description: "A living, breathing strategy document that persists across IDE sessions. It's not just a chat history; it's a structured database of your project's goals, milestones, and active tasks.",
    specs: [
      { label: "Storage Format", value: "Markdown + SQLite Sync" },
      { label: "Sync Protocol", value: "Real-time Delta Sync" },
      { label: "Context Window", value: "Infinite (Database-backed)" },
      { label: "Schema", value: "Universal Task Schema v1" }
    ],
    moat: "Chats are ephemeral. Strategies are forever. sideMCP is the only tool that maintains a persistent 'Plan of Record' that survives when you close the VS Code window."
  },
  "Market Knowledge (Stack)": {
    description: "Real-time intelligence on libraries, frameworks, and SaaS tools. We analyze thousands of hacker news threads and github repos to tell you 'what to use' before you write a single line of bad code.",
    specs: [
      { label: "Data Source", value: "Live Knowledge Graph" },
      { label: "Update Freq", value: "Daily Crawls" },
      { label: "Embedding", value: "OpenAI text-embedding-3-small" },
      { label: "Vector DB", value: "pgvector (Supabase)" }
    ],
    moat: "Cursor knows how to write code. sideMCP knows *what* code to write. We prevent technical debt by steering you toward winning technologies from Day 1."
  },
  "Decision Memory": {
    description: "A forensic audit trail of every technical decision you make. Why did you choose Postgres? Why did you switch to Tailwind? sideMCP remembers, so you don't have to defend your choices to investors later.",
    specs: [
      { label: "Record Type", value: "Immutable Log" },
      { label: "Query Engine", value: "Semantic Search + SQL" },
      { label: "Export Format", value: "JSON / PDF Report" },
      { label: "Privacy", value: "Local-First / Encrypted" }
    ],
    moat: "The 'Black Box' of your startup. When due diligence comes, you can generate a full report of your architectural maturity in seconds."
  },
  "Virtual User Testing": {
    description: "Simulate brutal, honest feedback from 50 distinct personas (e.g., 'Angry Senior Dev', 'The China User', 'The CFO') without shipping to production. Includes Regional & Executive archetypes.",
    specs: [
      { label: "Simulation", value: "LLM Persona Agents" },
      { label: "Persona Count", value: "50+ Pre-built Profiles" },
      { label: "Interaction", value: "Multi-turn Dialogue" },
      { label: "Output", value: "Actionable UX Report" }
    ],
    moat: "Don't wait for users to complain. Our virtual users will roast your product instantly, saving you weeks of feedback cycles."
  }
};

export default function Home() {
  const [activeCase, setActiveCase] = useState("auth");
  const [activeFeature, setActiveFeature] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText("pip install side-mcp");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };



  return (
    <div className="min-h-screen bg-black text-white selection:bg-white/20">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-black/50 backdrop-blur-md">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 bg-white rounded-sm" />
            <span className="font-bold tracking-tight">sideMCP</span>
          </div>
          <div className="flex items-center gap-6 text-sm font-medium text-zinc-400">
            <Link href="#difference" className="hover:text-white transition-colors">The Difference</Link>
            <Link href="#examples" className="hover:text-white transition-colors">Examples</Link>
            <Link href="#install" className="hover:text-white transition-colors">Install</Link>
            <Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link>
            <Link href="/login" className="flex items-center gap-2 text-white bg-white/10 px-4 py-2 rounded-full hover:bg-white/20 transition-all">
              Try Free <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </nav>

      <main>
        {/* Hero */}
        <section className="min-h-[85vh] flex flex-col items-center justify-center text-center px-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 text-xs text-zinc-400 mb-6 hover:bg-white/10 transition-colors cursor-default">
            <Zap className="w-3 h-3 text-yellow-400" />
            <span>The Strategic Kernel • Works alongside Cursor, Windsurf, Claude</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tighter mb-6 max-w-4xl mx-auto">
            Add sideMCP to your IDE.
          </h1>

          <p className="text-xl text-zinc-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Upgrade <strong>your IDE</strong> from a code editor <br className="hidden md:block" />
            to a <span className="text-white font-medium">Strategic Sidecar</span>.
          </p>
          <p className="text-sm text-zinc-500 mb-8 -mt-6">
            Native support for Cursor, Windsurf, Claude, and VS Code.
          </p>

          <div className="flex flex-col items-center gap-6">
            <button
              onClick={handleCopy}
              className="group relative h-16 pl-8 pr-6 rounded-full bg-white text-black font-semibold hover:bg-zinc-200 transition-all flex items-center gap-3 text-lg shadow-[0_0_40px_-5px_rgba(255,255,255,0.3)] hover:shadow-[0_0_60px_-10px_rgba(255,255,255,0.4)] hover:scale-105 active:scale-95"
            >
              <Terminal className="w-5 h-5 text-zinc-600 group-hover:text-black transition-colors" />
              <span className="font-mono tracking-tight mr-2">pip install side-mcp</span>
              {copied ? (
                <div className="bg-green-500 text-white text-xs px-2 py-1 rounded-full flex items-center gap-1 animate-in fade-in slide-in-from-left-2">
                  <Check className="w-3 h-3" /> Copied
                </div>
              ) : (
                <div className="w-8 h-8 rounded-full bg-black/5 flex items-center justify-center group-hover:bg-black/10 transition-colors">
                  <Copy className="w-4 h-4 text-zinc-500 group-hover:text-black" />
                </div>
              )}
            </button>
            <p className="text-xs text-zinc-600">
              One click to copy. Paste in your terminal.
            </p>
          </div>

          <div className="absolute bottom-10 animate-bounce text-zinc-600">
            <ChevronDown className="w-6 h-6 opacity-50" />
          </div>

          <div className="mt-16 flex flex-col items-center gap-4 animate-in fade-in slide-in-from-bottom-4 duration-1000 delay-200">
            <p className="text-zinc-500 text-sm italic">"The context that slips away when you close the tab."</p>
            <div className="flex flex-wrap justify-center gap-y-4 gap-x-8 text-sm text-zinc-500">
              <div className="flex items-center gap-2">
                <Brain className="w-4 h-4 text-zinc-400" />
                <span>Persistent Context</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-zinc-400" />
                <span>Strategic Guardrails</span>
              </div>
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-zinc-400" />
                <span>Market Intelligence</span>
              </div>
            </div>
          </div>
        </section>



        {/* The Honest Difference */}
        <section id="difference" className="py-20 px-6 border-t border-white/10">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-3xl font-bold tracking-tight text-center mb-4">The AI Development Stack</h2>
            <p className="text-zinc-400 text-center mb-16 max-w-2xl mx-auto">
              To build great software, you need three layers:<br />
              <span className="text-zinc-500">1. Execution (Cursor) • 2. Automation (Devin) • </span><strong className="text-white">3. Strategy (sideMCP)</strong>
            </p>

            {/* Honest Comparison */}
            <div className="overflow-x-auto mb-16 rounded-3xl border border-white/10 bg-zinc-900/30 p-1">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="py-4 px-6 text-zinc-400 font-medium tracking-wide text-sm uppercase">Capability</th>
                    <th className="py-4 px-6 text-center">
                      <span className="text-white font-bold tracking-tight">sideMCP (Strategy)</span>
                    </th>
                    <th className="py-4 px-6 text-center font-medium">Agents & IDEs (Execution)</th>
                  </tr>
                </thead>
                <tbody className="text-base text-sm">
                  <tr
                    onClick={() => setActiveFeature("Strategic Roadmap")}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors bg-white/[0.02] cursor-pointer group"
                  >
                    <td className="py-4 px-6 group-hover:pl-8 transition-all duration-300">
                      <div className="flex items-center gap-2">
                        <div>
                          <p className="font-medium text-white group-hover:text-blue-400 transition-colors flex items-center gap-2">
                            Strategic Roadmap (plan.md) <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                          </p>
                          <p className="text-sm text-zinc-500">Maintains context across sessions</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center gap-1.5 text-green-400 font-medium bg-green-500/10 px-3 py-1 rounded-full border border-green-500/20"><Check className="w-4 h-4" /> Project Lifecycle</span>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center gap-1.5 text-zinc-500 font-medium px-3 py-1 bg-zinc-800/50 rounded-full border border-white/5">Session Window</span>
                    </td>
                  </tr>
                  <tr
                    onClick={() => setActiveFeature("Market Knowledge")}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer group"
                  >
                    <td className="py-4 px-6 group-hover:pl-8 transition-all duration-300">
                      <p className="font-medium text-white group-hover:text-blue-400 transition-colors flex items-center gap-2">
                        Market Knowledge (Stack) <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </p>
                      <p className="text-sm text-zinc-500">"Don't build auth. Use Clerk."</p>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center justify-center gap-2 text-green-400 text-sm font-medium"><Check className="w-4 h-4" /> Live Knowledge Graph</span>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center justify-center gap-2 text-yellow-500 text-sm font-medium opacity-80">Generative (Static)</span>
                    </td>
                  </tr>
                  <tr
                    onClick={() => setActiveFeature("Deep Logic Graph")}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer group"
                  >
                    <td className="py-4 px-6 group-hover:pl-8 transition-all duration-300">
                      <p className="font-medium text-white group-hover:text-blue-400 transition-colors flex items-center gap-2">
                        Deep Logic Graph <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </p>
                      <p className="text-sm text-zinc-500">Maps classes, imports, and flows</p>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-green-500/10 text-green-400 border border-green-500/20 mx-auto"><Check className="w-4 h-4" /></span>
                    </td>
                    <td className="py-4 px-6 text-center">
                      <span className="inline-flex items-center gap-1.5 text-yellow-500 font-medium bg-yellow-500/10 px-3 py-1 rounded-full border border-yellow-500/20"><AlertCircle className="w-4 h-4" /> Partial</span>
                    </td>
                  </tr>
                  <tr
                    onClick={() => setActiveFeature("Decision Memory")}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer group"
                  >
                    <td className="py-4 px-6 group-hover:pl-8 transition-all duration-300">
                      <p className="font-medium text-white group-hover:text-blue-400 transition-colors flex items-center gap-2">
                        Decision Memory <ChevronRight className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </p>
                      <p className="text-sm text-zinc-500">"You chose Postgres on Jan 3"</p>
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
                        <div className="text-sm font-medium text-blue-300 mb-2 flex items-center gap-2">
                          <Zap className="w-4 h-4" /> The Moat
                        </div>
                        <p className="text-sm text-blue-100/80 leading-relaxed">
                          {CAPABILITY_SPECS[activeFeature].moat}
                        </p>
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
              <p className="text-xl text-white mb-4">
                <strong>Cursor + Devin + sideMCP</strong> = The Complete Stack.
              </p>
              <p className="text-zinc-400 mb-6">
                Let the agents write the code. We&apos;ll make sure they building the <em>right</em> thing.
              </p>
              <p className="text-xs text-zinc-600 border-t border-white/5 pt-4">
                * Unlike context search tools (Cody, Continue) which index <em>past</em> history, sideMCP maintains a forward-looking <strong>Decision Graph</strong>.
              </p>
            </div>
          </div>
        </section>

        {/* Moat Badges */}
        <section className="py-16 px-6 bg-zinc-900/30 border-y border-white/5">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-2xl font-bold tracking-tight text-center mb-12">What LLMs can&apos;t do (we can)</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center group cursor-default">
                <div className="w-16 h-16 rounded-full bg-blue-500/10 border border-blue-500/30 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 group-hover:bg-blue-500/20 transition-all duration-300">
                  <Brain className="w-8 h-8 text-blue-400" />
                </div>
                <p className="font-medium text-white group-hover:text-blue-400 transition-colors">Persistent Memory</p>
                <p className="text-xs text-zinc-500 mt-1">Decisions stored forever</p>
              </div>
              <div className="text-center group cursor-default">
                <div className="w-16 h-16 rounded-full bg-purple-500/10 border border-purple-500/30 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 group-hover:bg-purple-500/20 transition-all duration-300">
                  <Shield className="w-8 h-8 text-purple-400" />
                </div>
                <p className="font-medium text-white group-hover:text-purple-400 transition-colors">Strategic IQ</p>
                <p className="text-xs text-zinc-500 mt-1">Quantified health 0-160</p>
              </div>
              <div className="text-center group cursor-default">
                <div className="w-16 h-16 rounded-full bg-orange-500/10 border border-orange-500/30 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 group-hover:bg-orange-500/20 transition-all duration-300">
                  <Users className="w-8 h-8 text-orange-400" />
                </div>
                <p className="font-medium text-white group-hover:text-orange-400 transition-colors">Virtual Users</p>
                <p className="text-xs text-zinc-500 mt-1">Test on personas</p>
              </div>
              <div className="text-center group cursor-default">
                <div className="w-16 h-16 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 group-hover:bg-red-500/20 transition-all duration-300">
                  <Eye className="w-8 h-8 text-red-400" />
                </div>
                <p className="font-medium text-white group-hover:text-red-400 transition-colors">AST Forensics</p>
                <p className="text-xs text-zinc-500 mt-1">Real code analysis</p>
              </div>
            </div>
          </div>
        </section>

        {/* Examples - Perfect Moat Showcases */}
        <section id="examples" className="py-20 px-6">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold tracking-tight text-center mb-4">Killer Use Cases</h2>
            <p className="text-zinc-400 text-center mb-16">
              When CS0.ai saves you from a 2-week mistake effectively paying for itself forever.
            </p>

            <div className="bg-zinc-900/30 rounded-3xl border border-white/10 overflow-hidden">
              <div className="grid grid-cols-1 md:grid-cols-12 min-h-[500px]">
                {/* Left: Tabs */}
                <div className="md:col-span-4 border-r border-white/10 bg-black/20">
                  <div className="p-4 space-y-2">
                    {[
                      { id: "auth", icon: Shield, label: "The Auth Trap", save: "Saved 3 Weeks" },
                      { id: "research", icon: Globe, label: "Tech Radar", save: "Future Proofed" },
                      { id: "fork", icon: Brain, label: "Fork Strategy", save: "Saved 4 Days" },
                      { id: "pivot", icon: FileText, label: "The Pivot", save: "Saved Project" },
                      { id: "scale", icon: Zap, label: "Premature Scale", save: "Saved $400/mo" },
                      { id: "sec", icon: Eye, label: "Code Forensic", save: "Avoided Liability" }
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
                          <span className="font-medium text-sm">{tab.label}</span>
                        </div>
                        <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${activeCase === tab.id
                          ? "bg-green-500/20 text-green-400 border-green-500/30"
                          : "bg-zinc-800 border-zinc-700 opacity-30 grayscale"
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
                      <div className="bg-blue-600 text-white px-5 py-4 rounded-2xl rounded-br-none text-sm max-w-[85%] shadow-lg shadow-blue-900/20">
                        {activeCase === 'auth' && "Help me write a fast JWT auth middleware using HS256."}
                        {activeCase === 'research' && "Thinking of using Redux for the new dashboard state."}
                        {activeCase === 'fork' && "I need to build a documentation site for the API."}
                        {activeCase === 'pivot' && "Let's implement a viral waitlist invite system."}
                        {activeCase === 'scale' && "Setting up a Kubernetes cluster for the MVP deployment."}
                        {activeCase === 'sec' && "Just pushed the new stripe_webhook.py handler."}
                      </div>
                    </div>

                    {/* CSO Message */}
                    <div className="flex justify-start">
                      <div className="bg-zinc-800 border border-white/10 px-6 py-5 rounded-2xl rounded-bl-none max-w-[95%] shadow-xl">
                        <div className="font-mono text-sm leading-relaxed">
                          {/* AUTH CONTENT */}
                          {activeCase === 'auth' && <>
                            <p className="text-red-400 font-bold mb-3 flex items-center gap-2"><Shield className="w-4 h-4" /> ⛔ STRATEGIC INTERVENTION</p>
                            <p className="text-white mb-3">You are a team of 1. You cannot afford to maintain code-level auth.</p>
                            <div className="bg-black/30 p-3 rounded border border-white/5 mb-3">
                              <p className="text-zinc-400 mb-1">Recommendation:</p>
                              <div className="flex gap-2">
                                <span className="text-white bg-white/10 px-2 py-0.5 rounded text-xs">Clerk</span>
                                <span className="text-zinc-500">or</span>
                                <span className="text-white bg-white/10 px-2 py-0.5 rounded text-xs">Supabase Auth</span>
                              </div>
                            </div>
                            <p className="text-zinc-500 text-xs border-l-2 border-red-500/20 pl-3">
                              Reasoning: HS256 is symmetric (risky). Custom JWTs effectively have "forever bugs" regarding revocation.
                            </p>
                          </>}

                          {/* RESEARCH CONTENT (NEW) */}
                          {activeCase === 'research' && <>
                            <p className="text-cyan-400 font-bold mb-3 flex items-center gap-2"><Globe className="w-4 h-4" /> 📡 INDUSTRY PULSE</p>
                            <p className="text-white mb-3">Redux is declining for new greenfield projects. It introduces high boilerplate.</p>
                            <div className="bg-cyan-500/10 border border-cyan-500/20 p-3 rounded mb-3">
                              <p className="text-cyan-300 text-xs font-bold mb-1">STATE OF JS 2024 TRENDS:</p>
                              <div className="space-y-1">
                                <div className="flex justify-between text-xs">
                                  <span className="text-white">Zustand</span>
                                  <span className="text-green-400">▲ +22% Satisfaction</span>
                                </div>
                                <div className="flex justify-between text-xs">
                                  <span className="text-zinc-400">Redux</span>
                                  <span className="text-red-400">▼ -8% Retention</span>
                                </div>
                              </div>
                            </div>
                            <p className="text-zinc-400 text-xs">
                              Recommendation: Use <span className="text-white font-bold">Zustand</span> for global state, or <span className="text-white font-bold">TanStack Query</span> for server state.
                            </p>
                          </>}

                          {/* FORK CONTENT */}
                          {activeCase === 'fork' && <>
                            <p className="text-blue-400 font-bold mb-3 flex items-center gap-2"><Brain className="w-4 h-4" /> 💡 MARKET KNOWLEDGE</p>
                            <p className="text-white mb-3">Don't code this from scratch. It's a solved problem.</p>
                            <div className="grid grid-cols-2 gap-3 mb-3">
                              <div className="bg-green-500/10 border border-green-500/20 p-3 rounded hover:bg-green-500/20 transition-colors">
                                <p className="text-green-400 font-bold text-xs mb-1">Option A (Hosted)</p>
                                <p className="text-white">Mintlify</p>
                                <p className="text-zinc-500 text-[10px]">Free tier covers this.</p>
                              </div>
                              <div className="bg-white/5 border border-white/10 p-3 rounded hover:bg-white/10 transition-colors">
                                <p className="text-zinc-400 font-bold text-xs mb-1">Option B (Code)</p>
                                <p className="text-white">shadcn/taxonomy</p>
                                <p className="text-zinc-500 text-[10px]">Fork the repo.</p>
                              </div>
                            </div>
                            <p className="text-zinc-500 text-xs pl-1">
                              Saves estimated <span className="text-white">32 hours</span> of non-differentiating work.
                            </p>
                          </>}

                          {/* PIVOT CONTENT */}
                          {activeCase === 'pivot' && <>
                            <p className="text-purple-400 font-bold mb-3 flex items-center gap-2"><FileText className="w-4 h-4" /> 🛑 PLAN CONFLICT (plan.md)</p>
                            <p className="text-white mb-2">We pivoted to <strong>Enterprise B2B</strong> in Phase 2.</p>
                            <div className="bg-red-500/10 border border-red-500/20 p-3 rounded mb-3">
                              <p className="text-red-300 text-xs">Viral waitlists attract low-quality leads (Students/Indie Hackers), which hurts our "Sales-Led Growth" objective.</p>
                            </div>
                            <p className="text-yellow-400 font-bold mt-2 text-xs flex items-center gap-1">
                              <Check className="w-3 h-3" /> ALTERNATIVE: Build "Request Demo" form (HubSpot embed).
                            </p>
                          </>}

                          {/* SCALE CONTENT */}
                          {activeCase === 'scale' && <>
                            <p className="text-yellow-400 font-bold mb-3 flex items-center gap-2"><Zap className="w-4 h-4" /> ⚠️ PREMATURE SCALING</p>
                            <p className="text-white mb-3">You have 0 users. Kubernetes is pure overhead right now.</p>
                            <div className="bg-black/30 p-3 rounded border border-white/5 mb-3 space-y-2">
                              <div className="flex justify-between text-xs">
                                <span className="text-zinc-400">Kubernetes EKS</span>
                                <span className="text-red-400">~$140/mo + 20hrs</span>
                              </div>
                              <div className="flex justify-between text-xs">
                                <span className="text-white font-bold">Vercel / Railway</span>
                                <span className="text-green-400">$20/mo + 0hrs</span>
                              </div>
                            </div>
                            <p className="text-zinc-500 text-xs">
                              Switch to Docker/K8s only when monthly bill hits $500.
                            </p>
                          </>}

                          {/* FORENSIC CONTENT */}
                          {activeCase === 'sec' && <>
                            <p className="text-orange-400 font-bold mb-3 flex items-center gap-2"><Eye className="w-4 h-4" /> 🔍 AST FORENSIC ALERT</p>
                            <p className="text-white mb-3">I scanned `stripe_webhook.py`. Critical issue detected.</p>
                            <div className="font-mono text-[10px] bg-black p-3 rounded border border-red-500/30 text-red-300 mb-3 overflow-x-auto">
                              {`> Missing signature verification.\n> event = stripe.Event.construct_from(...) \n> ^ THIS IS FAKE.`}
                            </div>
                            <p className="text-white text-xs">
                              Attackers can spoof payment events.
                            </p>
                            <p className="text-green-400 text-xs mt-2 border-t border-white/10 pt-2">
                              Fix: Use `stripe.Webhook.construct_event` with `STRIPE_SIGNING_SECRET`.
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

        {/* The Strategic Brain (Refined & Moved) */}
        <section className="py-24 px-4 md:px-6 border-t border-white/10 bg-[#0c0c0e] relative overflow-hidden">

          <div className="max-w-[1200px] mx-auto relative z-10">
            <div className="text-center mb-10">
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4 text-white">The Brain of Your Project.</h2>
              <p className="text-lg text-zinc-400 max-w-2xl mx-auto">
                CSO.ai maintains a living <code className="text-zinc-300 bg-white/5 px-2 py-0.5 rounded border border-white/10">plan.md</code> in your repo. <br />
                It automatically tracks decisions, pivots, and constraints while you code.
              </p>
            </div>

            {/* IDE Container - Reformatted for "Geek/Simpler/Real" */}
            <div className="rounded-lg border border-white/10 bg-[#1e1e1e] shadow-2xl overflow-hidden font-mono text-sm relative flex flex-col h-[700px] max-h-[80vh] ring-1 ring-black/50">

              {/* 1. Title Bar (Simpler, Darker) */}
              <div className="h-9 bg-[#3c3c3c] flex items-center justify-between px-3 select-none border-b border-[#2b2b2b]">
                <div className="flex items-center gap-1.5 opacity-60 hover:opacity-100 transition-opacity">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" />
                  <div className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
                </div>
                <div className="text-[#cccccc] text-xs flex items-center gap-2">
                  <span className="opacity-50">hyperion-ledger —</span>
                  <span>plan.md</span>
                </div>
                <div className="w-10" />
              </div>

              <div className="flex flex-1 overflow-hidden">
                {/* 2. Activity Bar (Minimal) */}
                <div className="w-10 bg-[#333333] flex flex-col items-center py-3 gap-4 border-r border-[#2b2b2b]">
                  <Copy className="w-5 h-5 text-white opacity-90" />
                  <Eye className="w-5 h-5 text-[#858585]" />
                  <Brain className="w-5 h-5 text-[#858585]" />
                </div>

                {/* 3. Sidebar (Hyper-Real File Tree) */}
                <div className="w-56 bg-[#252526] flex flex-col border-r border-[#2b2b2b] hidden md:flex text-[12px]">
                  <div className="h-8 flex items-center px-3 text-[#bbbbbb] font-bold uppercase tracking-wider text-[10px] opacity-80">Explorer</div>
                  <div className="pt-1">
                    <div className="flex items-center gap-1 px-1 py-0.5 text-[#cccccc] font-bold">
                      <ChevronDown className="w-3 h-3" /> HYPERION-LEDGER
                    </div>
                    <div className="pl-3 mt-0.5 space-y-0.5 text-[#cccccc]">
                      <div className="flex items-center gap-1.5 px-2 py-0.5 opacity-80 hover:bg-[#2a2d2e] cursor-pointer">
                        <span className="text-[10px]">›</span> <span>core</span>
                      </div>
                      <div className="flex items-center gap-1.5 px-2 py-0.5 opacity-80 hover:bg-[#2a2d2e] cursor-pointer">
                        <span className="text-[10px]">›</span> <span>consensus</span>
                      </div>
                      <div className="flex items-center gap-1.5 px-2 py-0.5 bg-[#37373d] text-white cursor-pointer -ml-3 pl-5 border-l-2 border-[#007fd4]">
                        <FileText className="w-3 h-3 text-[#519aba]" /> <span>plan.md</span>
                      </div>
                      <div className="flex items-center gap-1.5 px-2 py-0.5 opacity-80 hover:bg-[#2a2d2e] cursor-pointer">
                        <FileText className="w-3 h-3 text-[#e37933]" /> <span>Cargo.toml</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 4. Editor (The Meat) */}
                <div className="flex-1 flex flex-col bg-[#1e1e1e]">
                  {/* Tabs */}
                  <div className="h-8 bg-[#252526] flex items-center">
                    <div className="h-full bg-[#1e1e1e] flex items-center gap-2 px-3 border-t border-[#007fd4] text-white text-xs pr-8 min-w-[120px]">
                      <FileText className="w-3 h-3 text-[#519aba]" />
                      <span>plan.md</span>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1 overflow-y-auto p-4 md:p-6 font-mono text-[13px] leading-relaxed text-[#d4d4d4]">

                    {/* Live Update Notification */}
                    <div className="absolute top-16 right-8 bg-[#252526] border border-[#007fd4] shadow-xl p-3 rounded-md flex items-start gap-3 w-72 animate-in fade-in slide-in-from-right-4 duration-700">
                      <div className="mt-0.5 w-2 h-2 rounded-full bg-[#007fd4] animate-pulse shadow-[0_0_8px_rgba(0,127,212,0.6)]" />
                      <div>
                        <h4 className="text-[11px] font-bold text-[#007fd4] uppercase mb-0.5">CSO.ai • Auto-Sync</h4>
                        <p className="text-[#a1a1a1] text-[11px]"> detected pivot to <span className="text-white">SOC2 Compliance</span>. Updating constraints...</p>
                      </div>
                    </div>

                    <div className="max-w-3xl">
                      <div className="flex items-baseline gap-2 mb-4">
                        <span className="text-[#569cd6] font-bold">#</span>
                        <h1 className="text-white font-bold text-lg">Hyperion Financial Ledger: Master Plan</h1>
                      </div>

                      <div className="border-l-2 border-[#4ec9b0] pl-4 py-1 mb-6 text-[#9cdcfe]">
                        <span className="text-[#569cd6] font-bold">&gt;&gt;</span> <strong className="text-white">Active Goal</strong>: Achieve SOC2 Type 1 Readiness by <span className="text-[#b5cea8]">Q1 2026</span>.<br />
                        <span className="text-[#569cd6] font-bold">&gt;&gt;</span> <strong className="text-white">Core Principle</strong>: "Immutable Logs Only. No Floating Point Math."
                      </div>

                      <div className="mb-8">
                        <div className="flex items-center gap-2 mb-2 text-[#d4d4d4]">
                          <span className="text-[#569cd6] font-bold">##</span>
                          <strong className="text-white">1. Strategic Constraints (The "Hard No")</strong>
                        </div>
                        <ul className="space-y-1">
                          <li className="flex gap-2">
                            <span className="text-[#6a9955]">-</span>
                            <span>[ ] <strong className="text-[#ce9178]">NO MongoDB</strong>: Financial data requires strict ACID compliance. Use <span className="text-[#b5cea8]">PostgreSQL</span> only.</span>
                          </li>
                          <li className="flex gap-2">
                            <span className="text-[#6a9955]">-</span>
                            <span>[ ] <strong className="text-[#ce9178]">NO JavaScript Math</strong>: All currency calcs must happen in Rust/WASM to prevent precision loss.</span>
                          </li>
                          <li className="flex gap-2 opacity-60">
                            <span className="text-[#6a9955] text-opacity-50">-</span>
                            <span className="line-through">[ ] NO External Auth</span> <span className="text-[#6a9955]">// DEPRECATED. We approved <span className="text-[#ce9178]">Clerk</span> on Jan 12.</span>
                          </li>
                        </ul>
                      </div>

                      <div className="mb-8">
                        <div className="flex items-center gap-2 mb-3 text-[#d4d4d4]">
                          <span className="text-[#569cd6] font-bold">##</span>
                          <strong className="text-white">2. Execution Roadmap</strong>
                        </div>

                        <div className="space-y-4">
                          {/* Phase 1 */}
                          <div className="opacity-50 hover:opacity-100 transition-opacity">
                            <div className="text-[#6a9955] font-bold mb-1">### Phase 1: The Core Ledger (Done)</div>
                            <ul className="pl-4 space-y-1">
                              <li className="text-[#808080]"><span className="text-[#6a9955]">[x]</span> Double-entry accounting engine (Rust)</li>
                              <li className="text-[#808080]"><span className="text-[#6a9955]">[x]</span> High-precision decimal library</li>
                            </ul>
                          </div>

                          {/* Phase 2 (Active) */}
                          <div className="bg-[#1e1e1e] border border-[#2b2b2b] p-3 -mx-3 rounded-md">
                            <div className="flex items-center justify-between mb-2">
                              <div className="text-[#4ec9b0] font-bold">### Phase 2: SOC2 & Auditing (Current)</div>
                              <span className="text-[10px] bg-[#4ec9b0]/10 text-[#4ec9b0] px-1.5 py-0.5 rounded border border-[#4ec9b0]/20">IN PROGRESS</span>
                            </div>
                            <ul className="pl-4 space-y-2">
                              <li className="flex gap-2 text-white">
                                <span className="text-[#6a9955] font-bold">[x]</span>
                                <span>Implement Audit Trail (pgAudit)</span>
                                <span className="text-[#808080] text-xs pt-1 ml-auto">// Completed yesterday</span>
                              </li>
                              <li className="flex gap-2 text-white">
                                <span className="text-[#dcdcaa] font-bold">[/]</span>
                                <span>Encryption at Rest (AWS KMS)</span>
                                <code className="text-[10px] bg-[#2d2d2d] px-1 py-0.5 rounded text-[#9cdcfe] ml-2">infra/terraform/kms.tf</code>
                              </li>
                              <li className="flex gap-2 text-white">
                                <span className="text-[#f44336] font-bold">[ ]</span>
                                <span>Disaster Recovery Drill</span>
                                <span className="text-[#f44336] text-[10px] bg-[#f44336]/10 px-1 py-0.5 rounded ml-2 border border-[#f44336]/20">BLOCKED by DevOps</span>
                              </li>
                            </ul>
                          </div>
                        </div>
                      </div>

                      <div className="border-t border-[#333333] pt-4 mt-8">
                        <div className="flex items-center gap-2 mb-2 text-[#d4d4d4]">
                          <span className="text-[#569cd6] font-bold">##</span>
                          <strong className="text-white">3. Context Memory (Key Decisions)</strong>
                        </div>
                        <div className="text-[12px] text-[#9da5b4] grid grid-cols-12 gap-2 border-b border-[#333333] pb-1 font-bold">
                          <div className="col-span-2">Date</div>
                          <div className="col-span-10">Record</div>
                        </div>
                        <div className="text-[12px] space-y-2 pt-2">
                          <div className="grid grid-cols-12 gap-2">
                            <div className="col-span-2 text-[#569cd6]">Jan 14</div>
                            <div className="col-span-10 text-[#d4d4d4]">Rejected <span className="text-[#ce9178]">Redis</span> for ledger locks. Reason: "Not durable enough for financial transactions."</div>
                          </div>
                          <div className="grid grid-cols-12 gap-2 bg-[#2d2d2d] -mx-2 px-2 py-1 rounded">
                            <div className="col-span-2 text-[#569cd6]">Jan 12</div>
                            <div className="col-span-10 text-[#d4d4d4]"><span className="text-[#b5cea8] font-bold">PIVOT:</span> Shifted focus from SMB to Enterprise. Added <span className="text-[#4ec9b0]">SOC2</span> requirements.</div>
                          </div>
                        </div>
                      </div>

                    </div>
                  </div>
                </div>
              </div>

              {/* 5. Status Bar (Authentic Blue) */}
              <div className="h-6 bg-[#007ad9] flex items-center justify-between px-3 text-white text-[11px] select-none">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1"><GitBranch className="w-3 h-3" /> main*</div>
                  <div className="flex items-center gap-1"><RefreshCw className="w-3 h-3 animate-spin duration-[3000ms]" /> Syncing...</div>
                  <div className="flex items-center gap-1 opacity-75"><AlertTriangle className="w-3 h-3" /> 0</div>
                </div>
                <div className="flex items-center gap-3 opacity-90">
                  <div>Ln 42, Col 12</div>
                  <div>UTF-8</div>
                  <div>Markdown</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Install Section */}
        <section id="install" className="py-20 px-6 bg-zinc-900/50">
          <div className="max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-4">Add to your IDE in 2 minutes</h2>
            <p className="text-zinc-400 text-center mb-12">Works alongside Cursor, Windsurf, Claude Desktop.</p>

            <div className="space-y-4">
              <div className="rounded-xl border border-white/10 bg-black p-5">
                <div className="flex items-center gap-3 mb-3">
                  <span className="w-7 h-7 rounded-full bg-white text-black font-bold flex items-center justify-center text-sm">1</span>
                  <span className="font-medium">Install</span>
                </div>
                <div className="bg-zinc-900 rounded-lg p-4 font-mono flex items-center justify-between">
                  <code className="text-green-400 text-lg">pip install cso-ai</code>
                  <button className="text-zinc-500 hover:text-white"><Copy className="w-5 h-5" /></button>
                </div>
              </div>

              <div className="rounded-xl border border-white/10 bg-black p-5">
                <div className="flex items-center gap-3 mb-3">
                  <span className="w-7 h-7 rounded-full bg-white text-black font-bold flex items-center justify-center text-sm">2</span>
                  <span className="font-medium">Add to MCP config</span>
                </div>
                <div className="bg-zinc-900 rounded-lg p-4 font-mono text-base overflow-x-auto">
                  <pre className="text-zinc-400">{`{
  "mcpServers": {
    "cso-ai": {
      "command": "python",
      "args": ["-m", "cso_ai.server"]
    }
  }
}`}</pre>
                </div>
              </div>

              <div className="rounded-xl border border-white/10 bg-black p-5">
                <div className="flex items-center gap-3 mb-3">
                  <span className="w-7 h-7 rounded-full bg-white text-black font-bold flex items-center justify-center text-sm">3</span>
                  <span className="font-medium">Start asking</span>
                </div>
                <div className="bg-zinc-900 rounded-lg p-4 font-mono">
                  <code className="text-blue-400 text-lg">&quot;Should I use microservices?&quot;</code>
                </div>
              </div>
            </div>

            <div className="mt-10 text-center">
              <Link href="/login" className="h-14 px-10 rounded-full bg-white text-black font-semibold hover:bg-zinc-200 transition-all inline-flex items-center gap-2 text-lg">
                Start Free <ChevronRight className="w-5 h-5" />
              </Link>
              <p className="text-zinc-500 text-sm mt-4">5,000 tokens/month free. No credit card.</p>
            </div>
          </div>
        </section>

        {/* Trust */}
        <section className="py-16 px-6 border-t border-white/10">
          <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <p className="text-3xl font-bold text-white mb-1">100%</p>
              <p className="text-zinc-500">Local-first</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-white mb-1">&lt;100ms</p>
              <p className="text-zinc-500">Cached responses</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-white mb-1">0</p>
              <p className="text-zinc-500">Data sent to cloud</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-white mb-1">MIT</p>
              <p className="text-zinc-500">Open source</p>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-white/10 py-10 px-6">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start gap-8">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <div className="h-4 w-4 bg-white rounded-sm" />
                <span className="font-bold">CSO.ai</span>
              </div>
              <p className="text-zinc-500 text-sm">The strategic memory layer for your IDE.</p>
            </div>
            <div className="flex gap-12 text-sm text-zinc-400">
              <div className="flex flex-col gap-2">
                <Link href="#difference" className="hover:text-white">The Difference</Link>
                <Link href="#examples" className="hover:text-white">Examples</Link>
                <Link href="#install" className="hover:text-white">Install</Link>
                <Link href="/pricing" className="hover:text-white">Pricing</Link>
              </div>
              <div className="flex flex-col gap-2">
                <Link href="https://github.com/erhanerdogan/cso-ai" className="hover:text-white">GitHub</Link>
                <Link href="/privacy" className="hover:text-white">Privacy</Link>
                <Link href="/terms" className="hover:text-white">Terms</Link>
              </div>
            </div>
          </div>
        </footer>

      </main>
    </div>
  );
}
