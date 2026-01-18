import Link from "next/link";

export default function PrivacyPage() {
    return (
        <div className="min-h-screen bg-black text-zinc-400 font-sans p-8 md:p-24 selection:bg-white/10">
            <div className="max-w-3xl mx-auto">
                <Link href="/" className="text-white hover:text-zinc-300 transition-colors mb-8 inline-block">
                    ← Back to CSO.ai
                </Link>

                <h1 className="text-4xl font-bold text-white mb-8 tracking-tight">Privacy Policy</h1>

                <div className="space-y-6 text-sm leading-relaxed">
                    <p className="text-zinc-500 font-mono">Last Updated: January 17, 2026</p>

                    <section>
                        <h2 className="text-xl font-semibold text-white mb-3">1. Local-First Philosophy</h2>
                        <p>Your code never leaves your machine. CSO.ai operates as a local MCP server. We only sync anonymized metadata (project hashes, decision summaries) to our global synchronization layer in Supabase to enable the dashboard features.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-white mb-3">2. Data Collection</h2>
                        <p>We collect project-level metadata to provide strategic intelligence. We do NOT collect PII (Personally Identifiable Information) such as your name, email, or IP address unless you explicitly sign up for a cloud account for billing purposes.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-white mb-3">3. Payments</h2>
                        <p>All payments are handled via Stripe. We do not store your credit card information. Stripe provides us with a unique customer ID and metadata to credit tokens to your local account.</p>
                    </section>

                    <p className="pt-8 border-t border-white/10 text-xs italic">
                        This is a strategic placeholder for the formal legal Privacy Policy.
                    </p>
                </div>
            </div>
        </div>
    );
}
