import { Check, ChevronRight, Zap, Shield, Brain, Users, Eye, Terminal, Building2 } from "lucide-react";
import Link from "next/link";

export default function PricingPage() {
    return (
        <div className="min-h-screen bg-black text-white selection:bg-white/20">
            {/* Navigation */}
            <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-black/50 backdrop-blur-md">
                <div className="max-w-7xl mx-auto flex items-center justify-between px-6 py-4">
                    <Link href="/" className="flex items-center gap-2">
                        <div className="h-6 w-6 bg-white rounded-sm" />
                        <span className="font-bold tracking-tight">CSO.ai</span>
                    </Link>
                    <div className="flex items-center gap-6 text-sm font-medium text-zinc-400">
                        <Link href="/#difference" className="hover:text-white transition-colors">Difference</Link>
                        <Link href="/pricing" className="text-white">Pricing</Link>
                        <Link href="/login" className="flex items-center gap-2 text-white bg-white/10 px-4 py-2 rounded-full hover:bg-white/20 transition-all">
                            Get Started <ChevronRight className="w-4 h-4" />
                        </Link>
                    </div>
                </div>
            </nav>

            <main className="pt-32 pb-16 px-6">
                <div className="max-w-6xl mx-auto">
                    {/* Header */}
                    <div className="text-center mb-16">
                        <h1 className="text-4xl md:text-6xl font-bold tracking-tighter mb-6">
                            All features free.<br />Pay only for tokens.
                        </h1>
                        <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
                            Use every feature from day one. Upgrade when you need more capacity.
                        </p>
                    </div>

                    {/* Pricing Cards - 3 tiers */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16 items-stretch">
                        {/* Free - All Features */}
                        <div className="relative p-8 rounded-3xl border border-white/10 bg-zinc-900/50 flex flex-col hover:border-white/20 transition-colors duration-300">
                            <div className="mb-6">
                                <h3 className="text-xl font-bold tracking-tight mb-2 text-white">Starter</h3>
                                <p className="text-zinc-400 text-sm">Try everything, no credit card</p>
                            </div>
                            <div className="mb-6">
                                <span className="text-5xl font-bold tracking-tighter text-white">$0</span>
                                <span className="text-zinc-400 font-medium">/forever</span>
                            </div>
                            <div className="mb-6 p-3 rounded-xl bg-green-500/10 border border-green-500/20">
                                <p className="text-green-400 text-sm font-medium flex items-center gap-2">
                                    <Check className="w-4 h-4" /> 5,000 tokens/month
                                </p>
                            </div>
                            <div className="flex-grow">
                                <ul className="space-y-3 mb-8 text-sm text-zinc-400">
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-green-400 shrink-0" />
                                        <span className="text-zinc-300">All 5 strategic tools</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-green-400 shrink-0" />
                                        <span className="text-zinc-300">Virtual User Lab</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-green-400 shrink-0" />
                                        <span className="text-zinc-300">Codebase X-Ray</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-green-400 shrink-0" />
                                        <span className="text-zinc-300">Mission Control (OKRs)</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-green-400 shrink-0" />
                                        <span className="text-zinc-300">Infinite memory</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-green-400 shrink-0" />
                                        <span className="text-zinc-300">Strategic IQ™</span>
                                    </li>
                                </ul>
                            </div>
                            <Link
                                href="/login"
                                className="w-full h-12 rounded-full border border-white/10 flex items-center justify-center font-medium hover:bg-white hover:text-black hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 mt-auto"
                            >
                                Start Free →
                            </Link>
                        </div>

                        {/* Pro - More Tokens */}
                        <div className="relative p-8 rounded-3xl border border-white/20 bg-zinc-900/80 flex flex-col hover:border-white/30 transition-colors duration-300 shadow-2xl shadow-blue-900/10">
                            <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-white text-black text-xs font-bold tracking-wider uppercase">
                                Most Popular
                            </div>
                            <div className="mb-6">
                                <h3 className="text-xl font-bold tracking-tight mb-2 text-white">Pro</h3>
                                <p className="text-zinc-400 text-sm">For power users</p>
                            </div>
                            <div className="mb-6">
                                <span className="text-5xl font-bold tracking-tighter text-white">$20</span>
                                <span className="text-zinc-400 font-medium">/month</span>
                            </div>
                            <div className="mb-6 p-3 rounded-xl bg-blue-500/10 border border-blue-500/20">
                                <p className="text-blue-400 text-sm font-medium flex items-center gap-2">
                                    <Check className="w-4 h-4" /> 50,000 tokens/month
                                </p>
                            </div>
                            <div className="flex-grow">
                                <ul className="space-y-3 mb-8 text-sm text-zinc-400">
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-green-400 shrink-0" />
                                        <span className="text-white font-medium">Everything in Starter</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-green-400 shrink-0" />
                                        <span className="text-zinc-300">10x more tokens</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-green-400 shrink-0" />
                                        <span className="text-zinc-300">Priority support</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-green-400 shrink-0" />
                                        <span className="text-zinc-300">Early access to features</span>
                                    </li>
                                </ul>
                            </div>
                            <Link
                                href="/login"
                                className="w-full h-12 rounded-full bg-white text-black flex items-center justify-center font-bold hover:bg-zinc-200 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 mt-auto"
                            >
                                Upgrade to Pro →
                            </Link>
                        </div>

                        {/* Enterprise - Contact Sales */}
                        <div className="relative p-8 rounded-3xl border border-white/10 bg-zinc-900/50 flex flex-col hover:border-white/20 transition-colors duration-300">
                            <div className="mb-6">
                                <h3 className="text-xl font-bold tracking-tight mb-2 flex items-center gap-2 text-white">
                                    <Building2 className="w-5 h-5" /> Enterprise
                                </h3>
                                <p className="text-zinc-400 text-sm">For teams that need more</p>
                            </div>
                            <div className="mb-6">
                                <span className="text-3xl font-bold tracking-tighter text-white">Custom</span>
                            </div>
                            <div className="mb-6 p-3 rounded-xl bg-purple-500/10 border border-purple-500/20">
                                <p className="text-purple-400 text-sm font-medium flex items-center gap-2">
                                    <Check className="w-4 h-4" /> Unlimited tokens
                                </p>
                            </div>
                            <div className="flex-grow">
                                <ul className="space-y-3 mb-8 text-sm text-zinc-400">
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-green-400 shrink-0" />
                                        <span className="text-white font-medium">Everything in Pro</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-green-400 shrink-0" />
                                        <span className="text-zinc-300">Shared team memory</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-green-400 shrink-0" />
                                        <span className="text-zinc-300">SSO/SAML</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-green-400 shrink-0" />
                                        <span className="text-zinc-300">Dedicated support</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-green-400 shrink-0" />
                                        <span className="text-zinc-300">Custom integrations</span>
                                    </li>
                                </ul>
                            </div>
                            <a
                                href="mailto:enterprise@cso.ai"
                                className="w-full h-12 rounded-full border border-white/10 flex items-center justify-center font-medium hover:bg-white hover:text-black hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 mt-auto"
                            >
                                Contact Sales →
                            </a>
                        </div>
                    </div>

                    {/* Key Message */}
                    <div className="text-center max-w-2xl mx-auto mb-16 p-6 rounded-2xl border border-white/10 bg-zinc-900/30">
                        <p className="text-lg text-white mb-2">
                            <strong>Product-first philosophy:</strong>
                        </p>
                        <p className="text-zinc-400">
                            We don&apos;t gate features. Use Virtual User Lab, Codebase X-Ray, and Mission Control from day one.
                            You&apos;ll upgrade when you need more capacity.
                        </p>
                    </div>

                    {/* Token Refills */}
                    <div className="text-center mb-16">
                        <div className="inline-block p-6 rounded-2xl border border-white/10 bg-zinc-900/30">
                            <p className="text-zinc-400 mb-2">
                                Need more tokens without subscribing?
                            </p>
                            <p className="text-white font-medium">
                                Buy refills anytime: <strong>$10 for 25,000 tokens</strong>
                            </p>
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="text-center">
                        <Link href="/" className="text-zinc-400 hover:text-white transition-colors">
                            ← Back to Home
                        </Link>
                    </div>
                </div>
            </main>
        </div>
    );
}
