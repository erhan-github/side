import { Calendar, GitCommit } from "lucide-react";

export const metadata = {
    title: "Changelog - Sidelith",
    description: "Product updates and release notes for Sidelith.",
};

export default function ChangelogPage() {
    const releases = [
        {
            version: "1.0.0",
            date: "2026-02-07",
            title: "Architecture Upgrade",
            changes: [
                "Refactored `PlanStore` to use recursive CTEs (Common Table Expressions) for O(1) hierarchy resolution.",
                "Replaced iterative Python loops with SQL-native recursive queries for dependency graph traversal.",
                "Enforced strict foreign key constraints on parent_id relationships.",
            ],
        },
        {
            version: "0.9.0",
            date: "2026-02-04",
            title: "Foundation Hardening",
            changes: [
                "Replaced `time.sleep` throttling with Token Bucket algorithm for precise rate limiting.",
                "Implemented `SignalBuffer` for unifying disparate logging streams into structured storage.",
                "Hardened storage permissions with AES-256 encryption handshake requirements.",
            ],
        },
        {
            version: "0.8.0",
            date: "2026-02-02",
            title: "IPC & Recovery",
            changes: [
                "Implemented local file-system based discovery for IDE sidecar processes.",
                "Added PII redaction middleware to telemetry pipeline.",
                "Created background recovery service for restoring context from crashed sessions.",
            ],
        },
        {
            version: "0.7.0",
            date: "2026-02-01",
            title: "Architectural Integrity",
            changes: [
                "Deployed `rejections.py` store for persisting architectural decision records (ADR).",
                "Implemented signal filtering service to reduce synchronization noise.",
                "Added network isolation toggle ('Airgap Mode') for strict local-only operation.",
            ],
        },
        {
            version: "0.6.0",
            date: "2026-01-31",
            title: "Context Awareness",
            changes: [
                "Decoupled monolithic coordinator into specialized component handlers.",
                "Implemented `ContextTracker` for non-blocking IDE cursor state monitoring.",
                "Standardized `project.json` schema for portable project identity.",
            ],
        },
        {
            version: "0.5.0",
            date: "2026-01-30",
            title: "Resource Accounting",
            changes: [
                "Established computational unit metrics for quantifying architectural debt.",
                "Implemented `averted_disasters` ledger to track return on investment for automated fixes.",
                "Created structured grant system for resource allocation tiers.",
            ],
        },
        {
            version: "0.4.0",
            date: "2026-01-29",
            title: "System Monitoring",
            changes: [
                "Implemented CPython audit hooks for low-latency system event monitoring.",
                "Integrated file watcher to detect real-time drift in project topology.",
                "Added telemetry endpoints for visualizing system load metrics.",
            ],
        },
        {
            version: "0.3.5",
            date: "2026-01-30",
            title: "Performance Optimization",
            changes: [
                "Optimized main event loop to reduce CPU overhead to <5%.",
                "Implemented non-blocking monitoring for system metrics.",
                "Refactored monolithic `simple_db` into modular persistence domains.",
            ],
        },
        {
            version: "0.3.0",
            date: "2026-01-28",
            title: "CLI Architecture",
            changes: [
                "Refactored CLI into modular handlers using Typer pattern.",
                "Implemented strictly typed environment configuration parsing.",
                "Added introspection subcommands for system status auditing.",
            ],
        },
        {
            version: "0.2.0",
            date: "2026-01-27",
            title: "Language Support",
            changes: [
                "Implemented file-signature based language detection.",
                "Deployed multi-stage architecture for code understanding.",
                "Standardized project fingerprinting across 15+ languages.",
            ],
        },
        {
            version: "0.1.5",
            date: "2026-01-26",
            title: "Local Intelligence",
            changes: [
                "Integrated generic LLM client interface for offline reasoning.",
                "Implemented multi-environment support (Local/Staging/Prod).",
                "Added vector embeddings support for semantic codebase analysis.",
            ],
        },
        {
            version: "0.1.0",
            date: "2026-01-24",
            title: "Genesis",
            changes: [
                "Initial repository scaffolding and dependency lockfile generation.",
                "Established SQLite-based local-first architecture with WAL mode enabled.",
                "Implemented cryptographic identity generation.",
            ],
        },
        {
            version: "0.0.1",
            date: "2026-01-16",
            title: "System Initialization",
            changes: [
                "Initial import of intelligence pipeline components.",
                "Established Model Context Protocol (MCP) server foundation.",
                "Implemented standard input/output transport layer.",
            ],
        },
    ];

    return (
        <main className="min-h-screen bg-[#050505] text-white pt-32 pb-20">
            <div className="max-w-4xl mx-auto px-6">
                {/* Header */}
                <div className="mb-16">
                    <h1 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60 mb-4">Changelog</h1>
                    <p className="text-xl text-white/60 text-balance">
                        Track our progress as we build the future of deterministic AI memory.
                    </p>
                </div>

                {/* Releases */}
                <div className="space-y-12">
                    {releases.map((release) => (
                        <div
                            key={release.version}
                            className="p-8 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-all"
                        >
                            {/* Release Header */}
                            <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
                                <div className="flex items-center gap-4">
                                    <div className="px-4 py-2 rounded-full bg-[var(--color-neon)]/10 border border-[var(--color-neon)]/20">
                                        <span className="text-[var(--color-neon)] font-mono font-bold text-sm">
                                            v{release.version}
                                        </span>
                                    </div>
                                    <h2 className="text-2xl font-bold text-white tracking-tight">{release.title}</h2>
                                </div>
                                <div className="flex items-center gap-2 text-white/40 text-sm font-medium">
                                    <Calendar size={16} />
                                    <span>{new Date(release.date).toLocaleDateString("en-US", {
                                        year: "numeric",
                                        month: "long",
                                        day: "numeric"
                                    })}</span>
                                </div>
                            </div>

                            {/* Changes */}
                            <ul className="space-y-3">
                                {release.changes.map((change, idx) => (
                                    <li key={idx} className="flex items-start gap-3 text-white/70 text-lg leading-relaxed">
                                        <GitCommit size={18} className="text-[var(--color-neon)] mt-1.5 flex-shrink-0" />
                                        <span>{change}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                {/* Footer Note */}
                <div className="mt-16 p-6 rounded-xl bg-white/[0.02] border border-white/5 text-center">
                    <p className="text-white/40 text-sm">
                        © 2026 Sidelith Inc. All systems functional.
                    </p>
                </div>
            </div>
        </main>
    );
}
