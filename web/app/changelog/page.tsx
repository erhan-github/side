import ChangelogList from "./ChangelogList";

export const metadata = {
    title: "Changelog - Sidelith",
    description: "Product updates and release notes for Sidelith.",
};

export default function ChangelogPage() {
    return (
        <main className="min-h-screen bg-[#050505] text-white pt-40 pb-20">
            <div className="max-w-7xl mx-auto px-6">
                <div className="max-w-4xl">
                    {/* Header */}
                    <div className="mb-12">
                        <h1 className="text-4xl font-extrabold text-white mb-6 tracking-tight">Changelog</h1>
                        <p className="text-lg text-zinc-400 leading-relaxed">
                            Track the evolution of the Sidelith System of Record.
                        </p>
                    </div>

                    {/* Interactive List */}
                    <ChangelogList />

                    {/* Footer Note */}
                    <div className="mt-16 p-6 rounded-xl bg-white/[0.02] border border-white/5 text-center">
                        <p className="text-white/40 text-sm">
                            © 2026 Sidelith Inc. All systems functional.
                        </p>
                    </div>
                </div>
            </div>
        </main>
    );
}
