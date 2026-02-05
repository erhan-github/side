import Link from "next/link";
import { ChevronRight } from "lucide-react";

export default function PrivacyPage() {
    return (
        <div className="min-h-screen bg-black text-zinc-400 font-sans p-8 md:p-24 selection:bg-white/10">
            <div className="max-w-3xl mx-auto">
                <Link href="/" className="mb-6 flex items-center gap-2 text-zinc-400 hover:text-white transition-colors">
                    <ChevronRight className="w-4 h-4 rotate-180" /> Back to Sidelith.com
                </Link>

                <h1 className="text-4xl font-bold text-white mb-8 tracking-tight">Privacy Policy</h1>

                <div className="space-y-6 text-sm leading-relaxed">
                    <p className="text-zinc-500 font-mono">Last Updated: February 4, 2026</p>

                    <section>
                        <h2 className="text-xl font-semibold text-white mb-3">1. Local-First Philosophy</h2>
                        <p>At Sidelith, we believe strategic intelligence shouldn't cost you your privacy. Your code never leaves your machine. Sidelith operates as a local MCP server. We only sync anonymized metadata (project hashes, decision summaries) to our global synchronization layer in Supabase to enable the dashboard features.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-white mb-3">2. Data Collection</h2>
                        <p>We collect project-level metadata to provide strategic intelligence. We do NOT collect PII (Personally Identifiable Information) such as your name, email, or IP address unless you explicitly sign up for a cloud account for billing purposes.</p>
                    </section>

                    <section>
                        <h2 className="text-xl font-semibold text-white mb-3">3. Payments</h2>
                        <p>All payments are handled via Lemon Squeezy. We do not store your credit card information. Lemon Squeezy acts as the Merchant of Record and provides us with a unique customer ID and metadata to credit tokens to your account.</p>
                    </section>

                    <p className="text-zinc-400 mb-8 italic">
                        Side is a privacy-first strategic intelligence platform. We believe your technical strategy is your most valuable secret.
                    </p>
                </div>
            </div>
        </div>
    );
}
