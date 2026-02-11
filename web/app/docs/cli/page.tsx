import { Header } from "@/components/Header";
import { LandingFooter } from "@/components/landing/LandingFooter";

export const metadata = {
    title: "CLI Reference | Sidelith",
    description: "Complete command reference for the Sidelith CLI.",
};

export default function CliPage() {
    return (
        <div className="min-h-screen bg-[#050505] text-white font-sans">
            <Header />

            <div className="max-w-7xl mx-auto px-6 pt-32 pb-20">
                <div className="max-w-4xl">
                    <div className="mb-16">
                        <h1 className="text-4xl md:text-5xl font-extrabold mb-6 font-heading tracking-tight">
                            CLI Reference
                        </h1>
                        <p className="text-xl text-zinc-400 mb-12 leading-relaxed">
                            All commands available in the Sidelith CLI.
                            <span className="text-xs text-zinc-600 ml-2">v{process.env.NEXT_PUBLIC_VERSION || '1.0.0'}</span>
                        </p>

                        <div className="space-y-12">
                            {/* Common Commands */}
                            <div>
                                <h2 className="text-xl font-bold text-emerald-500 uppercase tracking-widest mb-6">
                                    Common Commands
                                </h2>
                                <div className="overflow-hidden rounded-xl border border-white/10 bg-white/[0.02]">
                                    <table className="w-full text-left text-sm">
                                        <thead className="border-b border-white/5 bg-white/[0.02]">
                                            <tr>
                                                <th className="px-6 py-4 font-semibold text-white">Command</th>
                                                <th className="px-6 py-4 font-semibold text-white">Description</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-white/5">
                                            {[
                                                {
                                                    cmd: "side wizard",
                                                    desc: "Run interactive setup wizard"
                                                },
                                                {
                                                    cmd: "side login",
                                                    desc: "Authenticate with your Sidelith account"
                                                },
                                                {
                                                    cmd: "side connect",
                                                    desc: "Configure IDE integrations (Cursor, VS Code)"
                                                },
                                                {
                                                    cmd: "side status",
                                                    desc: "Check your tier, SU balance, and connection status"
                                                },
                                            ].map((row) => (
                                                <tr key={row.cmd} className="hover:bg-white/5 transition-colors">
                                                    <td className="px-6 py-4 font-mono text-emerald-400 font-bold">
                                                        {row.cmd}
                                                    </td>
                                                    <td className="px-6 py-4 text-zinc-400">
                                                        {row.desc}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            {/* Advanced Commands */}
                            <div>
                                <h2 className="text-xl font-bold text-zinc-500 uppercase tracking-widest mb-6">
                                    Advanced Commands
                                </h2>
                                <div className="overflow-hidden rounded-xl border border-white/10 bg-white/[0.02]">
                                    <table className="w-full text-left text-sm">
                                        <thead className="border-b border-white/5 bg-white/[0.02]">
                                            <tr>
                                                <th className="px-6 py-4 font-semibold text-white">Command</th>
                                                <th className="px-6 py-4 font-semibold text-white">Description</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-white/5">
                                            {[
                                                {
                                                    cmd: "side index",
                                                    desc: "Re-index your project (rebuilds context database)"
                                                },
                                                {
                                                    cmd: "side watch",
                                                    desc: "Auto-update context when you edit files"
                                                },
                                                {
                                                    cmd: "side audit",
                                                    desc: "Run security scan (checks for secrets, vulnerabilities)"
                                                },
                                                {
                                                    cmd: "side usage",
                                                    desc: "View detailed SU consumption and usage stats"
                                                },
                                                {
                                                    cmd: "side report",
                                                    desc: "Generate usage report (export as CSV)"
                                                },
                                                {
                                                    cmd: "side disconnect",
                                                    desc: "Remove Sidelith context for current project"
                                                },
                                            ].map((row) => (
                                                <tr key={row.cmd} className="hover:bg-white/5 transition-colors">
                                                    <td className="px-6 py-4 font-mono text-zinc-400 font-bold">
                                                        {row.cmd}
                                                    </td>
                                                    <td className="px-6 py-4 text-zinc-500">
                                                        {row.desc}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>

                        {/* Help Section */}
                        <div className="mt-16 pt-16 border-t border-white/10">
                            <h2 className="text-2xl font-bold mb-6 text-white tracking-tight">Need more help?</h2>
                            <div className="flex flex-wrap gap-6">
                                <a
                                    href="https://discord.gg/sidelith"
                                    className="flex items-center gap-2 text-emerald-400 hover:text-emerald-300 font-medium transition-colors"
                                >
                                    <span>Join Discord</span>
                                    <span>→</span>
                                </a>
                                <a
                                    href="mailto:support@sidelith.com"
                                    className="flex items-center gap-2 text-emerald-400 hover:text-emerald-300 font-medium transition-colors"
                                >
                                    <span>Email Support</span>
                                    <span>→</span>
                                </a>
                                <a
                                    href="/docs/troubleshooting"
                                    className="flex items-center gap-2 text-emerald-400 hover:text-emerald-300 font-medium transition-colors"
                                >
                                    <span>Troubleshooting Guide</span>
                                    <span>→</span>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <LandingFooter />
        </div>
    );
}
