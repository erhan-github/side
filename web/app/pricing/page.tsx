import { Check, Zap } from "lucide-react";
import Link from "next/link";
import { CheckoutButton } from "@/components/dashboard/CheckoutButton";

export default function PricingPage() {
    return (
        <div className="min-h-screen bg-black text-white">
            <main className="pt-40 pb-16">
                <div className="max-w-7xl mx-auto px-6">
                    {/* Header - FIXED */}
                    <div className="max-w-2xl mb-16">
                        <h1 className="text-5xl font-bold tracking-tight mb-6">
                            Pricing
                        </h1>
                        <p className="text-xl text-zinc-400">
                            Simple, usage-based pricing. Free to start, scale as you grow.
                        </p>
                    </div>

                    {/* Pricing Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-20">
                        {/* Hobby */}
                        <div className="p-6 rounded-2xl border border-white/10 bg-zinc-900/50 flex flex-col">
                            <div className="mb-4">
                                <h3 className="text-lg font-bold mb-1">Hobby</h3>
                                <p className="text-zinc-500 text-sm">For individuals</p>
                            </div>
                            <div className="mb-4">
                                <span className="text-4xl font-bold">$0</span>
                            </div>
                            <div className="mb-6 p-3 rounded-lg bg-zinc-800 border border-zinc-700">
                                <p className="text-sm text-zinc-300">
                                    500 Side Units/mo
                                </p>
                            </div>
                            <ul className="space-y-3 mb-6 flex-grow text-sm text-zinc-400">
                                <li className="flex items-start gap-2">
                                    <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                                    <span>Full context injection</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                                    <span>Local code indexing</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                                    <span>All IDE integrations</span>
                                </li>
                            </ul>
                            <Link
                                href="/login"
                                className="w-full h-10 rounded-full border border-white/20 flex items-center justify-center text-sm font-medium hover:bg-white hover:text-black transition-all"
                            >
                                Get Started
                            </Link>
                        </div>

                        {/* Pro */}
                        <div className="p-6 rounded-2xl border border-emerald-500/50 bg-emerald-500/5 flex flex-col shadow-xl">
                            <div className="mb-4">
                                <h3 className="text-lg font-bold mb-1">Pro</h3>
                                <p className="text-emerald-400 text-sm">For professionals</p>
                            </div>
                            <div className="mb-4">
                                <span className="text-4xl font-bold">$20</span>
                                <span className="text-zinc-500">/mo</span>
                            </div>
                            <div className="mb-6 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30">
                                <p className="text-sm text-emerald-300">
                                    5,000 Side Units/mo
                                </p>
                            </div>
                            <ul className="space-y-3 mb-6 flex-grow text-sm text-zinc-300">
                                <li className="flex items-start gap-2">
                                    <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                                    <span>10x more capacity</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                                    <span>Priority support</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                                    <span>Early access features</span>
                                </li>
                            </ul>
                            <CheckoutButton
                                variantId={process.env.NEXT_PUBLIC_LEMONSQUEEZY_VARIANT_ID_PRO!}
                                label="Upgrade to Pro"
                            />
                        </div>

                        {/* Elite */}
                        <div className="p-6 rounded-2xl border border-purple-500/50 bg-purple-500/5 flex flex-col shadow-xl">
                            <div className="mb-4">
                                <h3 className="text-lg font-bold mb-1">Elite</h3>
                                <p className="text-purple-400 text-sm">For power users</p>
                            </div>
                            <div className="mb-4">
                                <span className="text-4xl font-bold">$60</span>
                                <span className="text-zinc-500">/mo</span>
                            </div>
                            <div className="mb-6 p-3 rounded-lg bg-purple-500/10 border border-purple-500/30">
                                <p className="text-sm text-purple-300">
                                    25,000 Side Units/mo
                                </p>
                            </div>
                            <ul className="space-y-3 mb-6 flex-grow text-sm text-zinc-300">
                                <li className="flex items-start gap-2">
                                    <Check className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
                                    <span>50x more capacity</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Check className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
                                    <span>Direct engineer support</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Check className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
                                    <span>Private Slack channel</span>
                                </li>
                            </ul>
                            <CheckoutButton
                                variantId={process.env.NEXT_PUBLIC_LEMONSQUEEZY_VARIANT_ID_ELITE!}
                                label="Go Elite"
                                variant="purple"
                            />
                        </div>

                        {/* Enterprise */}
                        <div className="p-6 rounded-2xl border border-white/10 bg-zinc-900/50 flex flex-col">
                            <div className="mb-4">
                                <h3 className="text-lg font-bold mb-1">Enterprise</h3>
                                <p className="text-zinc-500 text-sm">For teams</p>
                            </div>
                            <div className="mb-4 h-[52px] flex items-center">
                                <span className="text-2xl font-bold">Custom</span>
                            </div>
                            <ul className="space-y-3 mb-6 flex-grow text-sm text-zinc-400">
                                <li className="flex items-start gap-2">
                                    <Check className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                                    <span>Unlimited units</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Check className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                                    <span>SSO & team management</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Check className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                                    <span>Centralized billing</span>
                                </li>
                            </ul>
                            <a
                                href="mailto:sales@sidelith.com"
                                className="w-full h-10 rounded-full border border-white/20 flex items-center justify-center text-sm font-medium hover:bg-white hover:text-black transition-all"
                            >
                                Contact Sales
                            </a>
                        </div>

                        {/* Airgapped */}
                        <div className="p-6 rounded-2xl border border-white/10 bg-zinc-900/50 flex flex-col">
                            <div className="mb-4">
                                <h3 className="text-lg font-bold mb-1">Airgapped</h3>
                                <p className="text-zinc-500 text-sm">On-premise</p>
                            </div>
                            <div className="mb-4 h-[52px] flex items-center">
                                <span className="text-2xl font-bold">Custom</span>
                            </div>
                            <ul className="space-y-3 mb-6 flex-grow text-sm text-zinc-400">
                                <li className="flex items-start gap-2">
                                    <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                                    <span>Self-hosted deployment</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                                    <span>Bring your own LLM</span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                                    <span>Zero cloud egress</span>
                                </li>
                            </ul>
                            <a
                                href="mailto:enterprise@sidelith.com"
                                className="w-full h-10 rounded-full border border-white/20 flex items-center justify-center text-sm font-medium hover:bg-white hover:text-black transition-all"
                            >
                                Contact Us
                            </a>
                        </div>
                    </div>

                    {/* Add-ons - FIXED */}
                    <div className="max-w-3xl mx-auto mb-16 p-8 rounded-2xl border border-white/10 bg-zinc-900/50">
                        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                            <div>
                                <h3 className="text-xl font-bold mb-2">Need more Side Units?</h3>
                                <p className="text-zinc-400 text-sm">
                                    Buy additional units anytime without upgrading your plan.
                                </p>
                            </div>
                            <div className="flex items-center gap-4 shrink-0">
                                <div className="text-center">
                                    <div className="text-3xl font-bold">$10</div>
                                    <div className="text-xs text-zinc-500">per pack</div>
                                </div>
                                <div className="h-8 w-px bg-white/10" />
                                <div className="text-center">
                                    <div className="text-3xl font-bold text-emerald-400">2,500</div>
                                    <div className="text-xs text-zinc-500">Side Units</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* FAQ - FIXED */}
                    <div className="max-w-2xl mx-auto">
                        <h2 className="text-2xl font-bold mb-8 text-center">Common Questions</h2>
                        <div className="space-y-6">
                            <div>
                                <h3 className="font-bold mb-2">What are Side Units?</h3>
                                <p className="text-zinc-400 text-sm">
                                    Side Units are our billing unit. 1 Side Unit = 1 AI context injection.
                                    Typical usage: 100-500 units per day for active development.
                                </p>
                            </div>
                            <div>
                                <h3 className="font-bold mb-2">Can I upgrade or downgrade anytime?</h3>
                                <p className="text-zinc-400 text-sm">
                                    Yes. Changes take effect immediately. Unused units roll over for one billing cycle.
                                </p>
                            </div>
                            <div>
                                <h3 className="font-bold mb-2">What happens if I run out?</h3>
                                <p className="text-zinc-400 text-sm">
                                    Context injection stops until your next billing cycle or you buy additional units.
                                    Your local index remains accessible.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
