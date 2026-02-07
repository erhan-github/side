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
            title: "The Sovereign Upgrade",
            changes: [
                "Implemented recursive CTE support in Task Dependency Engine for O(n) resolution.",
                "Refactored Memory Engine to use time-decay ranking algorithm (1/(t+1)).",
                "Implemented Merkle Tree aggregation service for 256-bit reasoning chain integrity.",
                "Enforced SHA-256 session token handshake on IPC Unix Domain Sockets.",
                "Standardized core services to strict Domain-Driven Design patterns.",
            ],
        },
        {
            version: "0.9.0",
            date: "2026-02-04",
            title: "Foundation Hardening",
            changes: [
                "Implemented token-bucket rate limiter for background process throttling.",
                "Unified disparate logging streams into a single structured SignalBuffer.",
                "Added unified stack trace parsing for Python, TypeScript, and Go runtimes.",
                "Added vacuum/pruning logic to SQLite engine to optimize storage footprint.",
            ],
        },
        {
            version: "0.8.0",
            date: "2026-02-02",
            title: "Neural Link",
            changes: [
                "Implemented local file-system based discovery for IDE sidecar processes.",
                "Added PII redaction middleware to telemetry pipeline.",
                "Deployed event bus listeners for cognitive friction analysis.",
                "Created background recovery service for restoring context from crashed sessions.",
            ],
        },
        {
            version: "0.7.5",
            date: "2026-02-01",
            title: "Cognitive Defense",
            changes: [
                "Deployed 'Strategic Graveyard' (rejections.py) for analyzing failed architectural branches.",
                "Implemented 'Cloud Distiller' service to filter low-entropy signals before sync.",
                "Added 'Airgap Mode' toggle for instant severance of all external network calls.",
            ],
        },
        {
            version: "0.7.0",
            date: "2026-01-31",
            title: "Context Awareness",
            changes: [
                "Decoupled monolithic `auto_intelligence` orchestrator into specialized component handlers.",
                "Implemented `ContextTracker` for non-blocking IDE cursor state monitoring.",
                "Standardized `project.json` schema for portable sovereign project identity.",
            ],
        },
        {
            version: "0.6.5",
            date: "2026-01-30",
            title: "Sovereign Economy",
            changes: [
                "Established 'Side Units' (SU) valuation metric for quantifying architectural debt.",
                "Implemented `averted_disasters` ledger to track ROI of automated fixes.",
                "Created 'Sovereign Grant' system for tier-based resource allocation.",
            ],
        },
        {
            version: "0.6.0",
            date: "2026-01-30",
            title: "The Sovereign Shell",
            changes: [
                "Implemented `side chat` REPL with `InteractiveUI` rendering engine.",
                "Deployed `SnitchMonitor` for real-time network transparency logging.",
                "Integrated `ShellEngine` controller loop for autonomous command execution.",
            ],
        },
        {
            version: "0.5.5",
            date: "2026-01-29",
            title: "Deep Silicon",
            changes: [
                "Implemented 'Pulse Engine' for zero-latency mmap-based system auditing.",
                "Integrated 'Fractal Watcher' to detect real-time drift in project topology.",
                "Added 'Mirror HUD' telemetry endpoints for visualizing cognitive load.",
            ],
        },
        {
            version: "0.5.0",
            date: "2026-01-30",
            title: "Performance Review",
            changes: [
                "Optimized main loop to reduce CPU overhead from 25% to <5%.",
                "Implemented non-blocking monitoring for system metrics (Silicon Velocity).",
                "Refactored monolithic `simple_db` into modular persistence domains.",
            ],
        },
        {
            version: "0.4.0",
            date: "2026-01-28",
            title: "Command Architecture",
            changes: [
                "Refactored CLI into modular `cli_handlers` using Typer pattern.",
                "Implemented strictly typed environment configuration parsing.",
                "Added `audit` and `status` subcommands for deep system introspection.",
            ],
        },
        {
            version: "0.3.0",
            date: "2026-01-27",
            title: "Polyglot Foundation",
            changes: [
                "Integrated Tree-sitter parsers for Python, TypeScript, and JavaScript.",
                "Implemented `SovereignParser` abstract interface for language-agnostic analysis.",
                "Deployed 'Trinity Architecture' (Sensor + Registry + Analyst) for code understanding.",
            ],
        },
        {
            version: "0.2.0",
            date: "2026-01-26",
            title: "Local Intelligence",
            changes: [
                "Integrated Ollama/Llama-2 for offline semantic reasoning.",
                "Implemented initial embeddings vector store using raw numpy arrays.",
                "Established multi-environment configuration (Dev/Staging/Prod).",
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
            title: "The Singularity",
            changes: [
                "Initial import of 'Antigravity' intelligence pipeline.",
                "Integrated 'Vector Embeddings' support for semantic codebase analysis.",
                "Established 'MCP Server' foundation with standard input/output transport.",
                "Deployed 'Market Analyzer' and 'LLM Strategist' agents.",
            ],
        },
    ];

    return (
        <main className="min-h-screen bg-void text-foreground pt-32 pb-20">
            <div className="max-w-4xl mx-auto px-6">
                {/* Header */}
                <div className="mb-16">
                    <h1 className="text-5xl font-bold text-white mb-4">Changelog</h1>
                    <p className="text-xl text-white/60">
                        Track our progress as we build the future of deterministic AI memory.
                    </p>
                </div>

                {/* Releases */}
                <div className="space-y-12">
                    {releases.map((release) => (
                        <div
                            key={release.version}
                            className="p-8 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all"
                        >
                            {/* Release Header */}
                            <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
                                <div className="flex items-center gap-4">
                                    <div className="px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                                        <span className="text-emerald-500 font-mono font-bold text-sm">
                                            v{release.version}
                                        </span>
                                    </div>
                                    <h2 className="text-2xl font-bold text-white">{release.title}</h2>
                                </div>
                                <div className="flex items-center gap-2 text-white/40 text-sm">
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
                                    <li key={idx} className="flex items-start gap-3 text-white/60">
                                        <GitCommit size={16} className="text-emerald-500 mt-1 flex-shrink-0" />
                                        <span>{change}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                {/* Footer Note */}
                <div className="mt-16 p-6 rounded-xl bg-blue-500/[0.05] border border-blue-500/10 text-center">
                    <p className="text-white/40 text-sm">
                        More updates coming soon. Follow us on{" "}
                        <a
                            href="https://github.com/sidelith"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-500 hover:underline"
                        >
                            GitHub
                        </a>{" "}
                        to stay updated.
                    </p>
                </div>
            </div>
        </main>
    );
}
