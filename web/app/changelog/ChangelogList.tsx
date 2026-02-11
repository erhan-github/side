"use client";

import { Calendar, GitCommit } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface ChangeItem {
    general: string;
    technical: string;
}

interface Release {
    version: string;
    date: string;
    title: string;
    changes: ChangeItem[];
}

export default function ChangelogList() {
    const releases: Release[] = [
        {
            version: "1.0.0",
            date: "2026-02-07",
            title: "Architecture Upgrade",
            changes: [
                {
                    general: "**Instant Task Loading:** Projects with thousands of tasks now load instantly, eliminating wait times during updates.",
                    technical: "**Recursive PlanStore Refactor:** Implemented SQL-native `WITH RECURSIVE` CTEs for O(1) retrieval of deeply nested task hierarchies."
                },
                {
                    general: "**Rock-Solid Reliability:** Creating or moving tasks is now glitch-free, even when you're working fast.",
                    technical: "**Graph Integrity Enforced:** Applied strict foreign-key constraints with `ON DELETE CASCADE` to prevent orphaned task nodes during rapid iteration."
                },
                {
                    general: "**Conflict-Free Sync:** Multiple updates happen smoothly without overriding each other's data.",
                    technical: "**Atomic Hierarchy Resolution:** Wrapped dependency graph traversal in `ISOLATION LEVEL SERIALIZABLE` transactions to guarantee state consistency."
                },
                {
                    general: "**94% Faster Performance:** The system feels almost instantaneous for complex operations.",
                    technical: "**Query Performance:** Reduced hierarchy resolution time by 94% by replacing iterative Python loops with database-native recursion."
                },
            ],
        },
        {
            version: "0.9.0",
            date: "2026-02-04",
            title: "Foundation Hardening",
            changes: [
                {
                    general: "**Smoother AI Responses:** The AI no longer gets 'stuck' or stutters when you send many requests at once.",
                    technical: "**Token Bucket Rate Limiting:** Replaced naive `time.sleep` throttling with a precise Token Bucket algorithm to smooth bursty API traffic."
                },
                {
                    general: "**Unified Logs:** All your system events, errors, and actions are now searchable in one place.",
                    technical: "**Unified Data Buffer:** Implemented `DataBuffer` to aggregate disparate logging streams (system, user, network) into a single structured storage pipeline."
                },
                {
                    general: "**Bank-Grade Security:** Your data is encrypted from the moment you start the application.",
                    technical: "**Encrypted Handshake:** Hardened storage permissions by enforcing AES-256 encryption requirements for all initial node handshakes."
                },
                {
                    general: "**Real-Time Data:** Updates happen instantly without slowing down your computer.",
                    technical: "**Zero-Latency Ingestion:** Optimized the `Pulse` engine to handle high-velocity telemetry ingestion with non-blocking I/O."
                },
            ],
        },
        {
            version: "0.8.0",
            date: "2026-02-02",
            title: "IPC & Recovery",
            changes: [
                {
                    general: "**Instant Crash Recovery:** If the system blinks, it's back in less than 2 seconds, right where you left off.",
                    technical: "**The Phoenix Protocol:** Introduced automated context regeneration (<2s) for instant recovery from system failures or crashes."
                },
                {
                    general: "**Zero Setup:** It just works. No complex configuration needed to connect your editor.",
                    technical: "**Sidecar Discovery:** Implemented local file-system based service discovery for zero-config IDE sidecar processes."
                },
                {
                    general: "**Privacy First:** Sensitive data like API keys are automatically stripped before leaving your machine.",
                    technical: "**PII Redaction Middleware:** Deployed a privacy layer that automatically scrubs sensitive data (API keys, emails) from telemetry pipelines before egress."
                },
                {
                    general: "**Smart Restart:** The system knows when to stop trying if something is fundamentally broken, preventing endless loops.",
                    technical: "**Crash Analysis:** Added a `CrashLoopBackoff` mechanism to prevent recursive restart loops during catastrophic failure modes."
                },
            ],
        },
        {
            version: "0.7.0",
            date: "2026-02-01",
            title: "Architectural Integrity",
            changes: [
                {
                    general: "**Decision Log:** Every major architectural choice is recorded, so you always know 'why' something was done.",
                    technical: "**Merkle-Chained Decision Ledgers:** Deployed `rejections.py` to cryptographically log architectural decision records (ADR) and rejections."
                },
                {
                    general: "**Focus Mode:** The system ignores noise and duplicate alerts, keeping your workspace clean.",
                    technical: "**Signal Filtering Service:** Implemented a noise-reduction layer using Jaccard Similarity to suppress duplicate or low-value system signals."
                },
                {
                    general: "**Airgap Mode:** For ultra-secure work, you can physically cut off all internet access with one switch.",
                    technical: "**Airgap Mode:** Added a strict network isolation toggle that physically disables all outbound HTTP requests for high-security environments."
                },
                {
                    general: "**Mistake Prevention:** The system catches circular logic errors before you even commit your code.",
                    technical: "**Invariant Enforcement:** Integrated automated checks for critical system invariants (e.g., no circular dependencies) into the commit hook."
                },
            ],
        },
        {
            version: "0.6.0",
            date: "2026-01-31",
            title: "Context Awareness",
            changes: [
                {
                    general: "**Smarter Coordination:** Different parts of the system now talk to each other more efficiently.",
                    technical: "**Decoupled Coordinator:** Refactored the monolithic `Coordinator` into specialized, independent handlers for improved fault isolation."
                },
                {
                    general: "**Mind Reader:** The AI anticipates what you need based on the file you're looking at.",
                    technical: "**ContextTracker Engine:** Implemented a non-blocking cursor state monitor to infer developer intent from active file focus."
                },
                {
                    general: "**Portable Projects:** Take your project 'Soul' with you to any machine without losing context.",
                    technical: "**Portable Identity Schema:** Standardized the `project.json` schema to allow project identity ('Soul') to be portable across different machines."
                },
                {
                    general: "**Intent Detection:** It understands what you're trying to do without you having to explain it.",
                    technical: "**Goal Tracking:** Added a 'MetaJSON' extractor to derive user intent from artifact modifications without requiring full LLM parsing."
                },
            ],
        },
        {
            version: "0.5.0",
            date: "2026-01-30",
            title: "Resource Accounting",
            changes: [
                {
                    general: "**Debt Tracker:** See exactly how much 'technical debt' your project is accumulating in real-time.",
                    technical: "**Computational Unit Metrics:** Established 'Side Units' (SU) to quantify and track the computational cost of architectural debt."
                },
                {
                    general: "**Value Calculator:** We track how much time the AI saves you on every automated fix.",
                    technical: "**ROI Ledger:** Implemented `averted_disasters` table to log and quantify the value of automated fixes in terms of saved engineering hours."
                },
                {
                    general: "**Fair Access:** Advanced features are unlocked as you level up your usage tier.",
                    technical: "**Tiered Grant System:** Created a structured capability grant system to manage access to high-cost features based on user tiers."
                },
                {
                    general: "**Cost Control:** Smart budgeting ensures you never accidentally overuse AI resources.",
                    technical: "**Budget Enforcement:** Added greedy token budgeting logic to ensure context window limits are never exceeded."
                },
            ],
        },
        {
            version: "0.4.0",
            date: "2026-01-29",
            title: "System Monitoring",
            changes: [
                {
                    general: "**Hyper-Fast Monitoring:** The system watches your project with zero lag.",
                    technical: "**CPython Audit Hooks:** Implemented low-level PEP 578 audit hooks to capture system events (file access, socket connections) with sub-millisecond latency."
                },
                {
                    general: "**Timeline View:** See events from every part of your stack in a single, unified timeline.",
                    technical: "**Polyglot Cross-Entropy Scavenging:** Added a log scavenger to correlate events across Next.js, Docker, and Python processes for unified audit timelines."
                },
                {
                    general: "**Drift Alert:** Get notified the moment your code starts to drift away from the plan.",
                    technical: "**Real-Time Drift Detection:** Integrated a file watcher to detect and alert on architectural drift (files created outside the plan) in real-time."
                },
                {
                    general: "**Live HUD:** Visualise your system's heartbeat in real-time.",
                    technical: "**Telemetry Visualization:** Added high-frequency telemetry endpoints to power the real-time 'Silicon Pulse' HUD."
                },
            ],
        },
        {
            version: "0.3.5",
            date: "2026-01-30",
            title: "Performance Optimization",
            changes: [
                {
                    general: "**Ultra Low CPU:** Sidelith runs silently in the background without eating up your battery.",
                    technical: "**<5% CPU Bound:** Optimized the main event loop to ensure the entire sidecar process consumes less than 5% CPU under normal load."
                },
                {
                    general: "**Instant Start:** The app launches immediately, loading heavy features only when needed.",
                    technical: "**Lazy Decoding Pipeline:** Implemented lazy loading for heavy assets and intelligence modules to reduce startup time."
                },
                {
                    general: "**Scalable Database:** The system handles massive projects without slowing down.",
                    technical: "**Modular Persistence:** Refactored the monolithic `simple_db` into specialized persistence domains (Strategic, Identity, Audit) for better scalability."
                },
                {
                    general: "**Smooth UI:** Background tasks never freeze or stutter your interface.",
                    technical: "**Non-Blocking Monitoring:** Moved system metrics collection to a background thread to prevent blocking the main execution path."
                },
            ],
        },
        {
            version: "0.3.0",
            date: "2026-01-28",
            title: "CLI Architecture",
            changes: [
                {
                    general: "**Powerful CLI:** Control everything from your terminal with simple, intuitive commands.",
                    technical: "**Modular CLI Handlers:** Refactored the CLI using the Typer pattern to support a plugin-like architecture for subcommands."
                },
                {
                    general: "**Safe Config:** The app checks your settings on startup to prevent weird errors later.",
                    technical: "**Strict Environment Parsing:** Implemented strict Pydantic models for parsing and validating `.env` configurations on startup."
                },
                {
                    general: "**Self-Diagnosis:** New tools allow the system to check its own health and report issues.",
                    technical: "**Introspection Tools:** Added `side audit` and `side status` subcommands for deep system introspection and debugging."
                },
            ],
        },
        {
            version: "0.2.0",
            date: "2026-01-27",
            title: "Language Support",
            changes: [
                {
                    general: "**Deep Understanding:** Sidelith reads your code structure, not just the text.",
                    technical: "**Deep Semantic Shadowing:** Implemented Tree-sitter AST extraction to build a live 'Semantic Shadow' of the codebase structure."
                },
                {
                    general: "**15+ Languages:** Works with almost any language you use, right out of the box.",
                    technical: "**Polyglot Fingerprinting:** Standardized project language detection across 15+ languages using file-signature analysis."
                },
                {
                    general: "**Smart Analysis:** A three-step process ensures nothing is missed.",
                    technical: "**Multi-Stage Understanding:** Deployed a multi-stage pipeline for code understanding: Detection -> Fingerprinting -> AST Parsing."
                },
            ],
        },
        {
            version: "0.1.5",
            date: "2026-01-26",
            title: "Local Intelligence",
            changes: [
                {
                    general: "**Offline AI:** Use powerful AI models without sending data to the cloud.",
                    technical: "**Offline Reasoning Kernel:** Integrated a generic LLM client interface to support offline inference via Ollama."
                },
                {
                    general: "**Any Environment:** Switch between laptop, server, and cloud setups instantly.",
                    technical: "**Multi-Environment Support:** Implemented configuration overlays for seamless switching between Local, Staging, and Production environments."
                },
                {
                    general: "**Semantic Search:** Find code by meaning, not just keyword matching.",
                    technical: "**Semantic Embeddings:** Added support for generating and storing vector embeddings to enable semantic search over the codebase."
                },
            ],
        },
        {
            version: "0.1.0",
            date: "2026-01-24",
            title: "Genesis",
            changes: [
                {
                    general: "**Instant Connect:** Connect your local environment to the mesh in seconds.",
                    technical: "**Zero-to-Connected Handshake:** Established the initial secure handshake protocol for connecting local nodes to the mesh in under 15 seconds."
                },
                {
                    general: "**Fast saving:** Your work is saved immediately and reliably.",
                    technical: "**SQLite WAL Architecture:** Initialized the local-first persistence layer using SQLite in Write-Ahead Logging (WAL) mode for concurrency."
                },
                {
                    general: "**Secure Identity:** Every node gets a unique, unforgeable cryptographic ID.",
                    technical: "**Cryptographic Identity:** Implemented local RSA key generation for establishing cryptographic node identity."
                },
            ],
        },
        {
            version: "0.0.1",
            date: "2026-01-16",
            title: "System Initialization",
            changes: [
                {
                    general: "**The Brain:** The core intelligence engine is online.",
                    technical: "**Intelligence Pipeline Boot:** Initial import of core intelligence modules and dependency injection container."
                },
                {
                    general: "**Standard Protocol:** Built on open standards for maximum compatibility.",
                    technical: "**MCP Foundation:** Established the Model Context Protocol (MCP) server foundation for standardized tool exposition."
                },
                {
                    general: "**Universal Talk:** Works with any editor that speaks standard IO.",
                    technical: "**STDIO Transport Layer:** Implemented the standard input/output transport layer for universal editor compatibility."
                },
            ],
        },
    ];

    return (
        <div className="space-y-12">
            {releases.map((release) => (
                <div
                    key={release.version}
                    className="p-8 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-all group"
                >
                    {/* Release Header */}
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
                        <div className="flex items-center gap-4">
                            <div className="px-4 py-2 rounded-full bg-[var(--color-neon)]/10 border border-[var(--color-neon)]/20 shadow-[0_0_15px_rgba(0,255,255,0.1)]">
                                <span className="text-[var(--color-neon)] font-mono font-bold text-sm">
                                    v{release.version}
                                </span>
                            </div>
                            <h2 className="text-2xl font-bold text-white tracking-tight">{release.title}</h2>
                        </div>
                        <div className="flex items-center gap-2 text-zinc-400 text-base font-medium">
                            <Calendar size={18} />
                            <span>{new Date(release.date).toLocaleDateString("en-US", {
                                year: "numeric",
                                month: "long",
                                day: "numeric"
                            })}</span>
                        </div>
                    </div>

                    {/* Interactions Hint */}
                    <div className="mb-6 flex items-center gap-2 text-xs text-zinc-600 font-mono uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                        <GitCommit size={12} />
                        <span>Hover to reveal technical details</span>
                    </div>

                    {/* Changes */}
                    <ul className="space-y-1">
                        {release.changes.map((change, idx) => (
                            <ChangelogItem key={idx} change={change} />
                        ))}
                    </ul>
                </div>
            ))}
        </div>
    );
}

function ChangelogItem({ change }: { change: ChangeItem }) {
    const [isHovered, setIsHovered] = useState(false);

    // Parse technical for bolding
    const techParts = change.technical.split("**");
    const techHasBold = techParts.length >= 3;

    // Parse general for bolding
    const genParts = change.general.split("**");
    const genHasBold = genParts.length >= 3;

    return (
        <li
            className="grid grid-cols-1 grid-rows-1 py-2 min-h-[3rem]"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            {/* General Version (Default) */}
            <div
                className={cn(
                    "col-start-1 row-start-1 flex items-start gap-4 text-zinc-300 text-lg leading-relaxed transition-all duration-300 ease-out",
                    isHovered ? "opacity-0 translate-y-2 pointer-events-none" : "opacity-100 translate-y-0"
                )}
            >
                <div className="mt-2.5 w-1.5 h-1.5 rounded-full bg-zinc-500 flex-shrink-0" />
                <span>
                    {genHasBold ? (
                        <>
                            <strong className="text-white font-semibold">{genParts[1]}</strong>
                            {genParts[2]}
                        </>
                    ) : (
                        change.general
                    )}
                </span>
            </div>

            {/* Technical Version (Hover) */}
            <div
                className={cn(
                    "col-start-1 row-start-1 flex items-start gap-4 text-zinc-400 text-lg leading-relaxed transition-all duration-300 ease-out",
                    isHovered ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-2 pointer-events-none"
                )}
            >
                <GitCommit size={20} className="text-[var(--color-neon)] mt-1 flex-shrink-0" />
                <span className="font-mono text-[0.95em]">
                    {techHasBold ? (
                        <>
                            <strong className="text-[var(--color-neon)] font-medium">{techParts[1]}</strong>
                            {techParts[2]}
                        </>
                    ) : (
                        change.technical
                    )}
                </span>
            </div>
        </li>
    );
}
