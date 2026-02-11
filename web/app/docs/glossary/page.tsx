"use client";

import { Header } from "@/components/Header";
import { LandingFooter } from "@/components/landing/LandingFooter";
import { Search, Book, Shield, Cpu, Database, FileText, Activity } from "lucide-react";
import { useState, useMemo } from "react";

// Definitions derived from glossary.md source of truth
const GLOSSARY_ITEMS = [
    {
        term: "AI Memory",
        category: "Core",
        definition: "Makes AI tools remember your project structure across sessions. When you use Cursor or VS Code, AI knows your folders, patterns, and architecture.",
        technical: "ContextService"
    },
    {
        term: "DNA",
        category: "Core",
        definition: "Your project's structural map. Sidelith analyzes your files to understand classes, functions, and how they connect in a machine-readable format.",
        technical: "TreeIndexer"
    },
    {
        term: "Code Rules",
        category: "Security",
        definition: "Your team's coding standards and patterns (e.g., 'Always use TypeScript strict mode').",
        technical: "SchemaStore"
    },
    {
        term: "Audit Log",
        category: "Security",
        definition: "A secure record of all Sidelith operations and usage history.",
        technical: "AuditService"
    },
    {
        term: "Project Documentation",
        category: "Intelligence",
        definition: "Your README and docs that explain what your project does. Sidelith reads these to understand your goals.",
        technical: "GoalTracker"
    },
    {
        term: "User Profile",
        category: "Identity",
        definition: "Manages project identity and developer preferences within Sidelith.",
        technical: "IdentityService"
    },
    {
        term: "Project Plan",
        category: "Intelligence",
        definition: "The store for long-term project decisions and roadmap items.",
        technical: "StrategicStore"
    },
    {
        term: "Side Units (SU)",
        category: "Billing",
        definition: "The standardized unit for Sidelith operations. 1 SU corresponds to a single intelligent context fulfillment.",
        technical: "Side Unit"
    },
    {
        term: "Billing Ledger",
        category: "Billing",
        definition: "A record of Side Unit consumption and billing transactions.",
        technical: "Ledger"
    },
    {
        term: "Activity Log",
        category: "System",
        definition: "A technical record of tool execution and system actions, used for debugging and transparency.",
        technical: "SystemEvent"
    },
    {
        term: "System Health",
        category: "Intelligence",
        definition: "Internal system awareness that monitors Sidelith's own health, memory usage, and performance metrics.",
        technical: "SystemAwareness"
    },
    {
        term: "System Cleanup",
        category: "System",
        definition: "Routine maintenance service that performs cleanup and optimization of the local index.",
        technical: "ContextEngine"
    },
    {
        term: "Persistent Context",
        category: "Concept",
        definition: "The ability for AI tools to retain awareness of your project's history, architecture, and goals across sessions.",
        technical: "Digital Amnesia Solution"
    },
    {
        term: "Tree-sitter Indexing",
        category: "Concept",
        definition: "High-precision code parsing that understands the actual structure of your code rather than just treating it as text.",
        technical: "AST Analysis"
    },
    {
        term: "Prompt Builder",
        category: "Core",
        definition: "Constructs optimized prompts by gathering relevant code and artifacts for the AI.",
        technical: "PromptBuilder"
    },
    {
        term: "History",
        category: "Intelligence",
        definition: "Processes repository commits and logs to build historical context.",
        technical: "HistoryAnalyzer"
    },
    {
        term: "Context Injection",
        category: "Concept",
        definition: "The process of providing relevant project information to your AI tool via MCP.",
        technical: "Context Injection"
    },
    {
        term: "MCP",
        category: "Protocol",
        definition: "Model Context Protocol. An open standard that enables AI tools to connect to external data sources like your codebase.",
        technical: "Model Context Protocol"
    },
    {
        term: "AST",
        category: "Protocol",
        definition: "Abstract Syntax Tree. A tree representation of the abstract syntactic structure of source code, used by Sidelith for precise indexing.",
        technical: "Abstract Syntax Tree"
    },
    {
        term: ".side/ Directory",
        category: "Concept",
        definition: "The local folder where Sidelith stores your project index. This stays on your machine and never gets uploaded.",
        technical: "Local Storage"
    },
    {
        term: "Context",
        category: "Concept",
        definition: "Information about your project (folder structure, patterns, decisions) that Sidelith provides to AI tools.",
        technical: "Context"
    },
    {
        term: "Cursor",
        category: "Tool",
        definition: "An AI-powered code editor that works with Sidelith via MCP.",
        technical: "IDE Integration"
    },
    {
        term: "VS Code",
        category: "Tool",
        definition: "Microsoft's code editor. Sidelith integrates via MCP to provide AI context.",
        technical: "IDE Integration"
    },
    {
        term: "Project Timeline",
        category: "Analysis",
        definition: "Chronological history of your project's development. Tracks major changes and decisions over time.",
        technical: "Timeline Store"
    },
    {
        term: "Pattern Sync",
        category: "Intelligence",
        definition: "Shares anonymized coding patterns to improve AI suggestions. Can be disabled in Settings.",
        technical: "Cloud Sync"
    },
    {
        term: "Error Context",
        category: "Analysis",
        definition: "Code surrounding an error (±10 lines) to help understand what went wrong.",
        technical: "Error Monitor"
    },
    {
        term: "Pattern Violations",
        category: "Security",
        definition: "Code that breaks your team's standards or architectural rules.",
        technical: "Rule Engine"
    },
    {
        term: "Context Snapshot",
        category: "Core",
        definition: "The atomic state of project intelligence injected into the AI tool. Contains the relevant code, rules, and historical context needed for a specific task.",
        technical: "ContextSnapshot"
    },
    {
        term: "Event Logger",
        category: "System",
        definition: "A resilient background recorder that tracks every project activity and AI interaction for auditability and reasoning reconstruction.",
        technical: "EventLogger"
    },
    {
        term: "Background Service",
        category: "System",
        definition: "A dedicated process for handling non-blocking project intelligence tasks like indexing and health monitoring.",
        technical: "BackgroundService"
    }
];

const CATEGORIES = ["All", "Core", "Security", "Intelligence", "Analysis", "Billing", "System", "Concept", "Protocol", "Tool"];

export default function GlossaryPage() {
    const [search, setSearch] = useState("");
    const [selectedCategory, setSelectedCategory] = useState("All");

    const filteredItems = useMemo(() => {
        return GLOSSARY_ITEMS.filter(item => {
            const matchesSearch = item.term.toLowerCase().includes(search.toLowerCase()) ||
                item.definition.toLowerCase().includes(search.toLowerCase());
            const matchesCategory = selectedCategory === "All" || item.category === selectedCategory;
            return matchesSearch && matchesCategory;
        }).sort((a, b) => a.term.localeCompare(b.term));
    }, [search, selectedCategory]);

    return (
        <div className="min-h-screen bg-[#050505] text-white font-sans">
            <Header />

            <div className="max-w-7xl mx-auto px-6 pt-32 pb-32">
                <div className="max-w-4xl mx-auto">
                    {/* Header */}
                    <div className="mb-12">
                        <div className="text-sm text-zinc-500 mb-4 flex items-center gap-2">
                            <a href="/docs" className="hover:text-zinc-300 transition-colors">Docs</a>
                            <span className="text-zinc-700">/</span>
                            <span className="text-white">Glossary</span>
                        </div>
                        <h1 className="text-4xl font-bold mb-6 tracking-tight">
                            Glossary
                        </h1>
                        <p className="text-lg text-zinc-400 leading-relaxed">
                            Common terms and concepts in Sidelith. If you see an unfamiliar word in our docs, look it up here.
                        </p>
                    </div>

                    {/* Search & Filter */}
                    <div className="mb-12 space-y-6">
                        <div className="relative">
                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                            <input
                                type="text"
                                placeholder="Search terms (e.g., 'Side Units', 'AST')..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="w-full bg-zinc-900/50 border border-white/10 rounded-xl py-4 pl-12 pr-4 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all"
                            />
                        </div>

                        <div className="flex flex-wrap gap-2">
                            {CATEGORIES.map(category => (
                                <button
                                    key={category}
                                    onClick={() => setSelectedCategory(category)}
                                    className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${selectedCategory === category
                                        ? "bg-emerald-600/20 text-emerald-400 border border-emerald-600/30"
                                        : "bg-zinc-900 border border-white/5 text-zinc-400 hover:text-white hover:bg-zinc-800"
                                        }`}
                                >
                                    {category}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Results */}
                    <div className="grid gap-6">
                        {filteredItems.map(item => (
                            <div key={item.term} className="p-6 rounded-xl border border-white/5 bg-zinc-900/20 hover:border-white/10 hover:bg-zinc-900/40 transition-all group">
                                <div className="flex items-start justify-between mb-3">
                                    <h3 className="text-xl font-bold text-white group-hover:text-emerald-400 transition-colors">
                                        {item.term}
                                    </h3>
                                    <span className="px-2 py-1 rounded-md bg-zinc-800 text-xs font-mono text-zinc-500 uppercase tracking-wider">
                                        {item.category}
                                    </span>
                                </div>
                                <p className="text-zinc-400 mb-4 leading-relaxed">
                                    {item.definition}
                                </p>
                                <div className="flex items-center gap-2 text-xs text-zinc-600 font-mono">
                                    <Activity className="w-3 h-3" />
                                    <span>Technical Term: </span>
                                    <code className="text-zinc-500">{item.technical}</code>
                                </div>
                            </div>
                        ))}

                        {filteredItems.length === 0 && (
                            <div className="text-center py-20 border border-dashed border-white/5 rounded-xl">
                                <p className="text-zinc-500">No terms found matching "{search}"</p>
                                <button
                                    onClick={() => { setSearch(""); setSelectedCategory("All"); }}
                                    className="mt-4 text-emerald-400 hover:text-emerald-300 text-sm font-medium"
                                >
                                    Clear filters
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <LandingFooter />
        </div>
    );
}
