import Link from "next/link";
import { ChevronLeft } from "lucide-react";

export default function TermsPage() {
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

                <h1 className="text-4xl font-bold text-white mb-4">Terms of Service</h1>
                <p className="text-sm text-zinc-600 mb-12">Last updated: February 11, 2026</p>

                <div className="space-y-8 text-sm leading-relaxed">
                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">1. Acceptance</h2>
                        <p>
                            By using Sidelith, you agree to these terms. If you don't agree,
                            please don't use the service.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">2. Service Description</h2>
                        <p>
                            Sidelith provides AI memory for your codebase. We index your project
                            structure locally and inject context into AI coding tools via the Model
                            Context Protocol (MCP).
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">3. Side Units & Billing</h2>
                        <p className="mb-4">
                            Side Units are our billing unit. 1 Side Unit = 1 AI context injection.
                        </p>
                        <ul className="list-disc list-inside space-y-2 text-zinc-400">
                            <li>Side Units are non-refundable once consumed</li>
                            <li>Unused units roll over for one billing cycle</li>
                            <li>You can upgrade, downgrade, or cancel anytime</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">4. Your Responsibilities</h2>
                        <p className="mb-4">You agree to:</p>
                        <ul className="list-disc list-inside space-y-2 text-zinc-400">
                            <li>Use the service legally and ethically</li>
                            <li>Not share your account credentials</li>
                            <li>Not attempt to reverse engineer the service</li>
                            <li>Not use the service to generate malicious code</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">5. AI Disclaimer</h2>
                        <p className="text-zinc-300 bg-yellow-500/10 border border-yellow-500/20 p-4 rounded-lg">
                            Sidelith uses AI. AI can make mistakes. Always review AI-generated
                            suggestions before implementing them. We are not responsible for code
                            generated using our service.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">6. Limitation of Liability</h2>
                        <p>
                            Sidelith is provided "as is" without warranties. Our liability is limited
                            to the amount you paid in the last 12 months. We are not liable for data
                            loss, business interruption, or consequential damages.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">7. Privacy & Data</h2>
                        <p>
                            Your code stays on your machine. We don't store your source code.
                            See our{" "}
                            <Link href="/privacy" className="text-white underline">
                                Privacy Policy
                            </Link>
                            {" "}for details.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">8. Termination</h2>
                        <p>
                            You can delete your account anytime. We may terminate accounts that
                            violate these terms. Upon termination, your data is deleted within 30 days.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">9. Changes to Terms</h2>
                        <p>
                            We may update these terms. We'll notify you via email 30 days before
                            major changes. Continued use means you accept the new terms.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">10. Contact</h2>
                        <p>
                            Questions?{" "}
                            <a href="mailto:legal@sidelith.com" className="text-white underline">
                                legal@sidelith.com
                            </a>
                        </p>
                    </section>

                    <section className="pt-8 border-t border-white/10">
                        <p className="text-xs text-zinc-600">
                            These terms are governed by the laws of Turkey.
                        </p>
                    </section>
                </div>
            </div>
        </div>
    );
}
