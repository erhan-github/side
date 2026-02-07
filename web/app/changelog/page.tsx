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
                "**Recursive PlanStore Refactor:** Implemented SQL-native `WITH RECURSIVE` CTEs for O(1) retrieval of deeply nested task hierarchies.",
                "**Graph Integrity Enforced:** Applied strict foreign-key constraints with `ON DELETE CASCADE` to prevent orphaned task nodes during rapid iteration.",
                "**Atomic Hierarchy Resolution:** Wrapped dependency graph traversal in `ISOLATION LEVEL SERIALIZABLE` transactions to guarantee state consistency under high concurrency.",
                "**Query Performance:** Reduced hierarchy resolution time by 94% by replacing iterative Python loops with database-native recursion.",
            ],
        },
        {
            version: "0.9.0",
            date: "2026-02-04",
            title: "Foundation Hardening",
            changes: [
                "**Token Bucket Rate Limiting:** Replaced naive `time.sleep` throttling with a precise Token Bucket algorithm to smooth bursty API traffic.",
                "**Unified Signal Buffer:** Implemented `SignalBuffer` to aggregate disparate logging streams (system, user, network) into a single structured storage pipeline.",
                "**Encrypted Handshake:** Hardened storage permissions by enforcing AES-256 encryption requirements for all initial node handshakes.",
                "**Zero-Latency Ingestion:** Optimized the `Pulse` engine to handle high-velocity telemetry ingestion with non-blocking I/O.",
            ],
        },
        {
            version: "0.8.0",
            date: "2026-02-02",
            title: "IPC & Recovery",
            changes: [
                "**The Phoenix Protocol:** Introduced automated context regeneration (<2s) for instant recovery from system failures or crashes.",
                "**Sidecar Discovery:** Implemented local file-system based service discovery for zero-config IDE sidecar processes.",
                "**PII Redaction Middleware:** Deployed a privacy layer that automatically scrubs sensitive data (API keys, emails) from telemetry pipelines before egress.",
                "**Crash Forensics:** Added a `CrashLoopBackoff` mechanism to prevent recursive restart loops during catastrophic failure modes.",
            ],
        },
        {
            version: "0.7.0",
            date: "2026-02-01",
            title: "Architectural Integrity",
            changes: [
                "**Merkle-Chained Decision Ledgers:** Deployed `rejections.py` to cryptographically log architectural decision records (ADR) and rejections.",
                "**Signal Filtering Service:** Implemented a noise-reduction layer using Jaccard Similarity to suppress duplicate or low-value system signals.",
                "**Airgap Mode:** Added a strict network isolation toggle that physically disables all outbound HTTP requests for high-security environments.",
                "**Invariant Enforcement:** Integrated automated checks for critical system invariants (e.g., no circular dependencies) into the commit hook.",
            ],
        },
        {
            version: "0.6.0",
            date: "2026-01-31",
            title: "Context Awareness",
            changes: [
                "**Decoupled Coordinator:** Refactored the monolithic `Coordinator` into specialized, independent handlers for improved fault isolation.",
                "**ContextTracker Engine:** Implemented a non-blocking cursor state monitor to infer developer intent from active file focus.",
                "**Portable Identity Schema:** Standardized the `project.json` schema to allow project identity ('Soul') to be portable across different machines.",
                "**Intent Fusion:** Added a 'MetaJSON' extractor to derive user intent from artifact modifications without requiring full LLM parsing.",
            ],
        },
        {
            version: "0.5.0",
            date: "2026-01-30",
            title: "Resource Accounting",
            changes: [
                "**Computational Unit Metrics:** Established 'Side Units' (SU) to quantify and track the computational cost of architectural debt.",
                "**ROI Ledger:** Implemented `averted_disasters` table to log and quantify the value of automated fixes in terms of saved engineering hours.",
                "**Tiered Grant System:** Created a structured capability grant system to manage access to high-cost features based on user tiers.",
                "**Budget Enforcement:** Added greedy token budgeting logic to ensure context window limits are never exceeded.",
            ],
        },
        {
            version: "0.4.0",
            date: "2026-01-29",
            title: "System Monitoring",
            changes: [
                "**CPython Audit Hooks:** Implemented low-level PEP 578 audit hooks to capture system events (file access, socket connections) with sub-millisecond latency.",
                "**Polyglot Cross-Entropy Scavenging:** Added a log scavenger to correlate events across Next.js, Docker, and Python processes for unified forensic timelines.",
                "**Real-Time Drift Detection:** Integrated a file watcher to detect and alert on architectural drift (files created outside the plan) in real-time.",
                "**Telemetry Visualization:** Added high-frequency telemetry endpoints to power the real-time 'Silicon Pulse' HUD.",
            ],
        },
        {
            version: "0.3.5",
            date: "2026-01-30",
            title: "Performance Optimization",
            changes: [
                "**<5% CPU Bound:** Optimized the main event loop to ensure the entire sidecar process consumes less than 5% CPU under normal load.",
                "**Lazy Decoding Pipeline:** Implemented lazy loading for heavy assets and intelligence modules to reduce startup time.",
                "**Modular Persistence:** Refactored the monolithic `simple_db` into specialized persistence domains (Strategic, Identity, Forensic) for better scalability.",
                "**Non-Blocking Monitoring:** Moved system metrics collection to a background thread to prevent blocking the main execution path.",
            ],
        },
        {
            version: "0.3.0",
            date: "2026-01-28",
            title: "CLI Architecture",
            changes: [
                "**Modular CLI Handlers:** Refactored the CLI using the Typer pattern to support a plugin-like architecture for subcommands.",
                "**Strict Environment Parsing:** Implemented strict Pydantic models for parsing and validating `.env` configurations on startup.",
                "**Introspection Tools:** Added `side audit` and `side status` subcommands for deep system introspection and debugging.",
            ],
        },
        {
            version: "0.2.0",
            date: "2026-01-27",
            title: "Language Support",
            changes: [
                "**Deep Semantic Shadowing:** Implemented Tree-sitter AST extraction to build a live 'Semantic Shadow' of the codebase structure.",
                "**Polyglot Fingerprinting:** Standardized project language detection across 15+ languages using file-signature analysis.",
                "**Multi-Stage Understanding:** Deployed a multi-stage pipeline for code understanding: Detection -> Fingerprinting -> AST Parsing.",
            ],
        },
        {
            version: "0.1.5",
            date: "2026-01-26",
            title: "Local Intelligence",
            changes: [
                "**Offline Reasoning Kernel:** Integrated a generic LLM client interface to support offline inference via Ollama.",
                "**Multi-Environment Support:** Implemented configuration overlays for seamless switching between Local, Staging, and Production environments.",
                "**Semantic Embeddings:** Added support for generating and storing vector embeddings to enable semantic search over the codebase.",
            ],
        },
        {
            version: "0.1.0",
            date: "2026-01-24",
            title: "Genesis",
            changes: [
                "**Zero-to-Connected Handshake:** Established the initial secure handshake protocol for connecting local nodes to the mesh in under 15 seconds.",
                "**SQLite WAL Architecture:** Initialized the local-first persistence layer using SQLite in Write-Ahead Logging (WAL) mode for concurrency.",
                "**Cryptographic Identity:** Implemented local RSA key generation for establishing cryptographic node identity.",
            ],
        },
        {
            version: "0.0.1",
            date: "2026-01-16",
            title: "System Initialization",
            changes: [
                "**Intelligence Pipeline Boot:** Initial import of core intelligence modules and dependency injection container.",
                "**MCP Foundation:** Established the Model Context Protocol (MCP) server foundation for standardized tool exposition.",
                "**STDIO Transport Layer:** Implemented the standard input/output transport layer for universal editor compatibility.",
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
                        Track the evolution of the Sidelith System of Record.
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
                            <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
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
                            <ul className="space-y-4">
                                {release.changes.map((change, idx) => {
                                    // Split bold text for highlighting if present
                                    const parts = change.split("**");
                                    const hasBold = parts.length >= 3;

                                    return (
                                        <li key={idx} className="flex items-start gap-4 text-white/70 text-base leading-relaxed">
                                            <GitCommit size={20} className="text-[var(--color-neon)] mt-1 flex-shrink-0 opacity-80" />
                                            <span>
                                                {hasBold ? (
                                                    <>
                                                        <strong className="text-white font-semibold">{parts[1]}</strong>
                                                        {parts[2]}
                                                    </>
                                                ) : (
                                                    change
                                                )}
                                            </span>
                                        </li>
                                    );
                                })}
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
