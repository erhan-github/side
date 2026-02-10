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
        definition: "The user-facing name for the Context Service. It orchestrates context retrieval and injection via MCP, giving your AI tools awareness of your codebase.",
        technical: "ContextService"
    },
    {
        term: "Project Scanner",
        category: "Core",
        definition: "The component that parses your code structure using Tree-sitter AST to create a local index.",
        technical: "CodeIndexer"
    },
    {
        term: "Code Guard",
        category: "Security",
        definition: "Enforces security and architectural policies in real-time to prevent unauthorized access or bad patterns.",
        technical: "RuleEngine"
    },
    {
        term: "Audit Log",
        category: "Security",
        definition: "A secure record of all Sidelith operations and usage history.",
        technical: "AuditService"
    },
    {
        term: "Goal Extractor",
        category: "Intelligence",
        definition: "Scans project documentation to extract and understand project goals and architectural decisions.",
        technical: "DocScanner"
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
        technical: "DecisionStore"
    },
    {
        term: "Side Units",
        category: "Billing",
        definition: "The billing unit for Sidelith operations. 1 Side Unit equals 1 AI context injection.",
        technical: "Side Unit (SU)"
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
        term: "Code Structure",
        category: "Core",
        definition: "A compressed Abstract Syntax Tree (AST) representation of your codebase, used for efficient context injection.",
        technical: "DNA"
    },
    {
        term: "System Cleanup",
        category: "System",
        definition: "Routine maintenance service that performs cleanup and optimization of the local index.",
        technical: "MaintenanceService"
    },
    {
        term: "Persistent Context",
        category: "Concept",
        definition: "The ability for AI tools to retain awareness of your project's history, architecture, and goals across sessions.",
        technical: "Digital Amnesia Solution"
    },
    {
        term: "Local Index",
        category: "Concept",
        definition: "The parsed code structure stored locally on your machine in the .side/ directory.",
        technical: "Fractal Memory"
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
        category: "Standard",
        definition: "Model Context Protocol. An open standard that enables AI tools to connect to external data sources like your codebase.",
        technical: "Model Context Protocol"
    },
    {
        term: "AST",
        category: "Standard",
        definition: "Abstract Syntax Tree. A tree representation of the abstract syntactic structure of source code, used by Sidelith for precise indexing.",
        technical: "Abstract Syntax Tree"
    },
    {
        term: "Local-First",
        category: "Concept",
        definition: "A design philosophy where data stays on the user's machine. Sidelith does not upload your source code to the cloud.",
        technical: "Zero-Leak Isolation"
    }
];

const CATEGORIES = ["All", "Core", "Security", "Intelligence", "Billing", "System", "Concept", "Standard"];

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
                            A standardized dictionary of Sidelith terminology. We use precise language to describe
                            how we handle your code and data.
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
                                    <span>Internal ID: </span>
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
