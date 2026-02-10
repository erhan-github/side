import { Check, ChevronRight, Zap, Shield, Brain, Users, Eye, Terminal, Building2 } from "lucide-react";
import Link from "next/link";
import { CheckoutButton } from "@/components/dashboard/CheckoutButton";

export default function PricingPage() {
    return (
        <div className="min-h-screen bg-black text-white selection:bg-white/20">
            <main className="pt-40 pb-16">
                <div className="max-w-7xl mx-auto px-6">
                    <div className="max-w-3xl">
                        {/* Header */}
                        <div className="mb-12">
                            <h1 className="text-4xl md:text-5xl font-black tracking-tighter mb-6 uppercase italic">
                                Infrastructure<br />Level.
                            </h1>
                            <p className="text-lg text-zinc-400 leading-relaxed">
                                The System of Record for Project Context. Sidelith is a foundational layer for your IDE. Free for individuals, tiered for scale.
                            </p>
                        </div>
                    </div>
                </div>

                <div className="max-w-7xl mx-auto px-6">


                    {/* Pricing Cards - 5 tiers */}
                    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-20 items-stretch">
                        {/* Hobby - Free */}
                        <div className="relative p-6 rounded-3xl border border-white/10 bg-zinc-900/50 flex flex-col hover:border-white/20 transition-colors duration-300">
                            <div className="mb-4">
                                <h3 className="text-lg font-bold tracking-tight mb-1 text-white uppercase tracking-widest">Hobby</h3>
                                <p className="text-zinc-400 text-xs font-medium">Individual, evaluation</p>
                            </div>
                            <div className="mb-4">
                                <span className="text-4xl font-bold tracking-tighter text-white">$0</span>
                            </div>
                            <div className="mb-4 p-2 rounded-lg bg-zinc-500/10 border border-zinc-500/20">
                                <p className="text-zinc-300 text-xs font-medium flex items-center gap-2">
                                    <Check className="w-3 h-3" /> 500 SUs / mo
                                </p>
                            </div>
                            <div className="flex-grow">
                                <ul className="space-y-3 mb-6 text-xs text-zinc-300 font-medium">
                                    <li className="flex items-center gap-2">
                                        <Check className="w-3 h-3 text-cyan-400 shrink-0" />
                                        <span>Full Context Injection</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-3 h-3 text-cyan-400 shrink-0" />
                                        <span>Local SQLite Registry</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-3 h-3 text-cyan-400 shrink-0" />
                                        <span>All IDE Integrations</span>
                                    </li>
                                </ul>
                            </div>
                            <Link href="/login" className="w-full h-10 rounded-full border border-white/10 flex items-center justify-center text-sm font-bold hover:bg-white hover:text-black transition-all">Start</Link>
                        </div>

                        {/* Pro - $20 */}
                        <div className="relative p-6 rounded-3xl border border-cyan-500/30 bg-zinc-900/80 flex flex-col hover:border-cyan-500/50 transition-colors duration-300 shadow-xl shadow-cyan-900/10 z-10">
                            <div className="mb-4">
                                <h3 className="text-lg font-bold tracking-tight mb-1 text-white uppercase tracking-widest">Pro</h3>
                                <p className="text-cyan-300 text-xs font-medium">Professional developers</p>
                            </div>
                            <div className="mb-4">
                                <span className="text-4xl font-bold tracking-tighter text-white">$20</span>
                            </div>
                            <div className="mb-4 p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
                                <p className="text-cyan-200 text-xs font-medium flex items-center gap-2">
                                    <Check className="w-3 h-3" /> 5,000 SUs / mo
                                </p>
                            </div>
                            <div className="flex-grow">
                                <ul className="space-y-3 mb-6 text-xs text-zinc-200 font-medium">
                                    <li className="flex items-center gap-2">
                                        <Check className="w-3 h-3 text-cyan-400 shrink-0" />
                                        <span>High-Volume Throughput</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-3 h-3 text-cyan-400 shrink-0" />
                                        <span>Priority Support</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-3 h-3 text-cyan-400 shrink-0" />
                                        <span>Early Access Features</span>
                                    </li>
                                </ul>
                            </div>
                            <CheckoutButton variantId={process.env.NEXT_PUBLIC_LEMONSQUEEZY_VARIANT_ID_PRO!} label="UPGRADE" />
                        </div>

                        {/* Elite - $60 */}
                        <div className="relative p-6 rounded-3xl border border-purple-500/30 bg-zinc-900/80 flex flex-col hover:border-purple-500/50 transition-colors duration-300 shadow-xl shadow-purple-900/10 z-20">
                            <div className="mb-4">
                                <h3 className="text-lg font-bold tracking-tight mb-1 text-white uppercase tracking-widest">Elite</h3>
                                <p className="text-purple-300 text-xs font-medium">Power users, small teams</p>
                            </div>
                            <div className="mb-4">
                                <span className="text-4xl font-bold tracking-tighter text-white">$60</span>
                            </div>
                            <div className="mb-4 p-2 rounded-lg bg-purple-500/10 border border-purple-500/20">
                                <p className="text-purple-200 text-xs font-medium flex items-center gap-2">
                                    <Check className="w-3 h-3" /> 25,000 SUs / mo
                                </p>
                            </div>
                            <div className="flex-grow">
                                <ul className="space-y-3 mb-6 text-xs text-zinc-200 font-medium">
                                    <li className="flex items-center gap-2">
                                        <Check className="w-3 h-3 text-purple-400 shrink-0" />
                                        <span>Maximum Throughput</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-3 h-3 text-purple-400 shrink-0" />
                                        <span>Direct Engineer Support</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-3 h-3 text-purple-400 shrink-0" />
                                        <span>Private Slack Channel</span>
                                    </li>
                                </ul>
                            </div>
                            <CheckoutButton variantId={process.env.NEXT_PUBLIC_LEMONSQUEEZY_VARIANT_ID_ELITE!} label="GO ELITE" variant="purple" />
                        </div>

                        {/* Enterprise - Custom */}
                        <div className="relative p-6 rounded-3xl border border-blue-500/20 bg-zinc-900/50 flex flex-col hover:border-blue-500/40 transition-colors duration-300">
                            <div className="mb-4">
                                <h3 className="text-lg font-bold tracking-tight mb-1 text-white uppercase tracking-widest">Enterprise</h3>
                                <p className="text-blue-300 text-xs font-medium">Teams, SSO, Shared Pools</p>
                            </div>
                            <div className="mb-4 flex flex-col justify-center h-10">
                                <span className="text-2xl font-bold tracking-tighter text-white">Custom</span>
                            </div>
                            <div className="flex-grow">
                                <ul className="space-y-3 mb-6 text-xs text-zinc-300 font-medium">
                                    <li className="flex items-center gap-2">
                                        <Check className="w-3 h-3 text-blue-400 shrink-0" />
                                        <span>Shared Context Pools</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-3 h-3 text-blue-400 shrink-0" />
                                        <span>SAML SSO / Enforcement</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-3 h-3 text-blue-400 shrink-0" />
                                        <span>Centralized Billing</span>
                                    </li>
                                </ul>
                            </div>
                            <a href="mailto:sales@sidelith.com" className="w-full h-10 rounded-full border border-white/10 flex items-center justify-center text-sm font-bold hover:bg-white hover:text-black transition-all mt-auto">Contact</a>
                        </div>

                        {/* Airgapped - Custom */}
                        <div className="relative p-6 rounded-3xl border border-emerald-500/20 bg-zinc-900/50 flex flex-col hover:border-emerald-500/40 transition-colors duration-300">
                            <div className="mb-4">
                                <h3 className="text-lg font-bold tracking-tight mb-1 text-white uppercase tracking-widest">Airgapped</h3>
                                <p className="text-emerald-300 text-xs font-medium">Regulated industries</p>
                            </div>
                            <div className="mb-4 flex flex-col justify-center h-10">
                                <span className="text-2xl font-bold tracking-tighter text-white">Custom</span>
                            </div>
                            <div className="flex-grow">
                                <ul className="space-y-2 mb-6 text-xs text-zinc-400">
                                    <li className="flex items-center gap-2">
                                        <Check className="w-3 h-3 text-emerald-400 shrink-0" />
                                        <span>On-Premise Deployment</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-3 h-3 text-emerald-400 shrink-0" />
                                        <span>BYOK LLM / Local</span>
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <Check className="w-3 h-3 text-emerald-400 shrink-0" />
                                        <span>Zero Cloud Egress</span>
                                    </li>
                                </ul>
                            </div>
                            <a href="mailto:enterprise@sidelith.com" className="w-full h-10 rounded-full border border-white/10 flex items-center justify-center text-sm font-medium hover:bg-white hover:text-black transition-all mt-auto">Available Now</a>
                        </div>
                    </div>

                    {/* Add-on Pricing */}
                    <div className="max-w-4xl mx-auto mb-16 px-8 py-10 rounded-3xl border border-white/10 bg-zinc-900/30 backdrop-blur-sm relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                            <Zap className="w-24 h-24 text-white" />
                        </div>
                        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
                            <div className="text-center md:text-left">
                                <h3 className="text-2xl font-black tracking-tighter uppercase italic mb-2">Structural Refills</h3>
                                <p className="text-zinc-400 text-sm max-w-sm">
                                    Ran out of throughput mid-sprint? Scale incrementally without changing your phase.
                                </p>
                            </div>
                            <div className="flex items-center gap-6">
                                <div className="text-center">
                                    <div className="text-3xl font-black tracking-tighter text-white font-mono">$10</div>
                                    <div className="text-[10px] uppercase tracking-widest text-zinc-500 font-bold">Price</div>
                                </div>
                                <div className="h-10 w-[1px] bg-white/10" />
                                <div className="text-center">
                                    <div className="text-3xl font-black tracking-tighter text-cyan-400 font-mono">2,500</div>
                                    <div className="text-[10px] uppercase tracking-widest text-zinc-500 font-bold">Extra SUs</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Key Message */}
                    <div className="text-center max-w-2xl mx-auto mb-16 p-8 rounded-3xl border border-white/10 bg-zinc-900/30">
                        <p className="text-zinc-400 italic">
                            "Modern engineering is not about typing. It's about structure. Sidelith provides the stable System of Record required for high-stakes architectural decisions."
                        </p>
                    </div>
                </div>
            </main>
        </div>
    );
}
