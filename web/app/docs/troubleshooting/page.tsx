import { Header } from "@/components/Header";
import { LandingFooter } from "@/components/landing/LandingFooter";

export const metadata = {
    title: "Troubleshooting | Sidelith",
    description: "Common issues and solutions for Sidelith.",
};

export default function TroubleshootingPage() {
    return (
        <div className="min-h-screen bg-[#050505] text-white font-sans">
            <Header />

            <div className="max-w-7xl mx-auto px-6 pt-32 pb-20">
                <div className="max-w-3xl">
                    <div className="mb-16">
                        <h1 className="text-4xl md:text-5xl font-bold mb-6 font-heading">
                            Troubleshooting
                        </h1>
                        <p className="text-xl text-zinc-400 mb-12">
                            Common issues you might encounter and how to resolve them.
                        </p>

                        <div className="space-y-6">
                            <div className="p-8 rounded-xl bg-white/[0.02] border border-white/10">
                                <h3 className="text-xl font-bold text-white mb-3 font-heading">"No active session found"</h3>
                                <p className="text-zinc-400 mb-4">
                                    This error occurs if you try to run a command that requires authentication but haven't logged in yet.
                                </p>
                                <div className="bg-black border border-white/10 p-4 rounded-lg font-mono text-sm text-emerald-400">
                                    side login
                                </div>
                            </div>

                            <div className="p-8 rounded-xl bg-white/[0.02] border border-white/10">
                                <h3 className="text-xl font-bold text-white mb-3 font-heading">"No supported IDEs automatically detected"</h3>
                                <p className="text-zinc-400 mb-4">
                                    Sidelith looks for Cursor, VS Code, and Claude Desktop in their default installation paths. If you installed them in a custom location, you may need to configure the path manually or reinstall to the default location.
                                </p>
                                <div className="bg-black border border-white/10 p-4 rounded-lg font-mono text-sm text-zinc-500">
                                    /Applications/Cursor.app
                                </div>
                            </div>

                            <div className="p-8 rounded-xl bg-white/[0.02] border border-white/10">
                                <h3 className="text-xl font-bold text-white mb-3 font-heading">"[config] is invalid JSON"</h3>
                                <p className="text-zinc-400 mb-4">
                                    This usually means your `settings.json` file has a syntax error (like a missing comma). Sidelith tries to patch it safely, but if the file is already corrupt, it will abort to avoid data loss.
                                </p>
                            </div>
                        </div>

                        <div className="mt-16 pt-16 border-t border-white/10">
                            <h2 className="text-2xl font-bold mb-6 text-white font-heading">Still stuck?</h2>
                            <div className="flex flex-wrap gap-6">
                                <a href="https://discord.gg/sidelith" className="flex items-center gap-2 text-emerald-400 hover:text-emerald-300 font-medium transition-colors">
                                    <span>Join Discord Community</span>
                                    <span>→</span>
                                </a>
                                <a href="mailto:support@sidelith.com" className="flex items-center gap-2 text-emerald-400 hover:text-emerald-300 font-medium transition-colors">
                                    <span>Email Support</span>
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
