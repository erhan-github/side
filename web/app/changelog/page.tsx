import ChangelogList from "./ChangelogList";

export const metadata = {
    title: "Changelog - Sidelith",
    description: "Product updates and release notes for Sidelith.",
};

export default function ChangelogPage() {
    return (
        <main className="min-h-screen bg-[#050505] text-white pt-32 pb-20">
            <div className="max-w-4xl mx-auto px-6">
                {/* Header */}
                <div className="mb-16">
                    <h1 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60 mb-4 pb-2">Changelog</h1>
                    <p className="text-xl text-white/60 text-balance">
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
        </main>
    );
}
