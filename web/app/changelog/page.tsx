import { Calendar, GitCommit } from "lucide-react";

export const metadata = {
    title: "Changelog - Sidelith",
    description: "Product updates and release notes for Sidelith.",
};

export default function ChangelogPage() {
    const releases = [
        {
            version: "0.1.0",
            date: "2026-02-06",
            title: "Initial Release",
            changes: [
                "Fractal Merkle Tree indexing for codebase understanding",
                "MCP server integration for Cursor and Claude Desktop",
                "Sovereign Units (SUs) pricing model",
                "Local-first SQLite persistence",
                "Forensic audit system",
                "CLI tools: feed, audit, status",
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
