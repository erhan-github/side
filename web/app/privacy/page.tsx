import Link from "next/link";
import { ChevronLeft } from "lucide-react";

export default function PrivacyPage() {
    return (
        <div className="min-h-screen bg-black text-zinc-400 p-8 md:p-24">
            <div className="max-w-3xl mx-auto">
                <Link
                    href="/"
                    className="mb-8 flex items-center gap-2 text-zinc-500 hover:text-white transition-colors"
                >
                    <ChevronLeft className="w-4 h-4" />
                    Back to Sidelith
                </Link>

                <h1 className="text-4xl font-bold text-white mb-4">Privacy Policy</h1>
                <p className="text-sm text-zinc-600 mb-12">Last updated: February 11, 2026</p>

                <div className="space-y-8 text-sm leading-relaxed">
                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">1. What We Collect</h2>
                        <p className="mb-4">
                            Sidelith is local-first. Your code never leaves your machine. We only collect:
                        </p>
                        <ul className="list-disc list-inside space-y-2 text-zinc-400">
                            <li>Email address (for account authentication)</li>
                            <li>Usage metrics (Side Unit consumption for billing)</li>
                            <li>Project metadata (anonymized hashes, not code)</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">2. How We Use Your Data</h2>
                        <p className="mb-4">We use your data to:</p>
                        <ul className="list-disc list-inside space-y-2 text-zinc-400">
                            <li>Provide the Sidelith service</li>
                            <li>Process billing and payments</li>
                            <li>Send service updates (you can opt out)</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">3. What We Never Collect</h2>
                        <ul className="list-disc list-inside space-y-2 text-zinc-400">
                            <li>Your source code</li>
                            <li>File paths or names</li>
                            <li>Git history</li>
                            <li>Environment variables or secrets</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">4. Third-Party Services</h2>
                        <p className="mb-4">We use:</p>
                        <ul className="list-disc list-inside space-y-2 text-zinc-400">
                            <li><strong>Supabase</strong> - Authentication and database</li>
                            <li><strong>Lemon Squeezy</strong> - Payment processing</li>
                            <li><strong>Vercel</strong> - Hosting</li>
                        </ul>
                        <p className="mt-4 text-zinc-500">
                            These services have their own privacy policies. We don't share your data
                            with any other third parties.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">5. Data Retention</h2>
                        <p>
                            We keep your account data as long as your account is active. You can delete
                            your account anytime from the dashboard, which removes all associated data
                            within 30 days.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">6. Your Rights</h2>
                        <p className="mb-4">You have the right to:</p>
                        <ul className="list-disc list-inside space-y-2 text-zinc-400">
                            <li>Access your data</li>
                            <li>Delete your account and data</li>
                            <li>Export your data</li>
                            <li>Opt out of marketing emails</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">7. Compliance</h2>
                        <p>
                            Sidelith complies with GDPR, CCPA, and other privacy regulations.
                            For questions, contact{" "}
                            <a href="mailto:privacy@sidelith.com" className="text-white underline">
                                privacy@sidelith.com
                            </a>
                        </p>
                    </section>

                    <section className="pt-8 border-t border-white/10">
                        <p className="text-zinc-500 italic">
                            Your code is yours. We're just here to help AI remember it.
                        </p>
                    </section>
                </div>
            </div>
        </div>
    );
}
