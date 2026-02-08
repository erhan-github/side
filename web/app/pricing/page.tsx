import { Check, ChevronRight, Zap, Shield, Brain, Users, Eye, Terminal, Building2 } from "lucide-react";
import Link from "next/link";
import { CheckoutButton } from "@/components/dashboard/CheckoutButton";

export default function PricingPage() {
    return (
        <div className="min-h-screen bg-black text-white selection:bg-white/20">
            <main className="pt-32 pb-16 px-6">
                <div className="max-w-6xl mx-auto">
                    {/* Header */}
                    <div className="text-center mb-16">
                        <h1 className="text-4xl md:text-6xl font-black tracking-tighter mb-6 uppercase italic">
                            Infrastructure<br />Level.
                        </h1>
                        <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
                            The System of Record for Project Context. Sidelith is a foundational layer for your IDE. Free for individuals, tiered for scale.
                        </p>
                    </div>

                    {/* Pricing Cards - 4 tiers */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16 items-stretch">
                        {/* Hobby - Free */}
                        <div className="relative p-8 rounded-3xl border border-white/10 bg-zinc-900/50 flex flex-col hover:border-white/20 transition-colors duration-300">
                            <div className="mb-6">
                                <h3 className="text-xl font-bold tracking-tight mb-2 text-white uppercase tracking-widest">Hobby</h3>
                                <p className="text-zinc-400 text-sm italic">For individuals</p>
                            </div>
                            <div className="mb-6">
                                <span className="text-5xl font-bold tracking-tighter text-white">$0</span>
                                <span className="text-zinc-400 font-medium">/mo</span>
                            </div>
                            <div className="mb-6 p-3 rounded-xl bg-zinc-500/10 border border-zinc-500/20">
                                <p className="text-zinc-400 text-sm font-medium flex items-center gap-2">
                                    <Check className="w-4 h-4" /> 500 SUs / MO
                                </p>
                            </div>
                            <div className="flex-grow">
                                <ul className="space-y-3 mb-8 text-sm text-zinc-400">
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-cyan-400 shrink-0" />
                                        <span className="text-zinc-300">Decision Database</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-cyan-400 shrink-0" />
                                        <span className="text-zinc-300">Forensic Audit Logs</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-cyan-400 shrink-0" />
                                        <span className="text-zinc-300">Local SQLite Registry</span>
                                    </li>
                                </ul>
                            </div>
                            <Link
                                href="/login"
                                className="w-full h-12 rounded-full border border-white/10 flex items-center justify-center font-medium hover:bg-white hover:text-black hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 mt-auto"
                            >
                                Get Started →
                            </Link>
                        </div>

                        {/* Pro - $20 */}
                        <div className="relative p-8 rounded-3xl border border-cyan-500/30 bg-zinc-900/80 flex flex-col hover:border-cyan-500/50 transition-colors duration-300 shadow-2xl shadow-cyan-900/10 z-10">
                            <div className="mb-6">
                                <h3 className="text-xl font-black tracking-tight mb-2 text-white uppercase tracking-widest italic">Pro</h3>
                                <p className="text-cyan-400/60 text-sm italic">For professionals</p>
                            </div>
                            <div className="mb-6">
                                <span className="text-6xl font-black tracking-tighter text-white">$20</span>
                                <span className="text-zinc-400 font-medium">/mo</span>
                            </div>
                            <div className="mb-6 p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20">
                                <p className="text-cyan-400 text-sm font-medium flex items-center gap-2">
                                    <Check className="w-4 h-4" /> 5,000 SUs / MO
                                </p>
                            </div>
                            <div className="flex-grow">
                                <ul className="space-y-3 mb-8 text-sm text-zinc-300">
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-cyan-400 shrink-0" />
                                        <span className="font-bold text-white">Everything in Hobby</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-cyan-400 shrink-0" />
                                        <span>Architectural Forensics</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-cyan-400 shrink-0" />
                                        <span>Continuous Context Sync</span>
                                    </li>
                                </ul>
                            </div>
                            <CheckoutButton
                                variantId={process.env.LEMONSQUEEZY_VARIANT_ID_PRO!}
                                label="UPGRADE"
                            />
                        </div>

                        {/* Elite - $60 */}
                        <div className="relative p-8 rounded-3xl border border-purple-500/30 bg-zinc-900/80 flex flex-col hover:border-purple-500/50 transition-colors duration-300 shadow-2xl shadow-purple-900/10 scale-105 z-20">
                            <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-purple-500 text-white text-[10px] font-black tracking-[0.2em] uppercase">
                                Best Value
                            </div>
                            <div className="mb-6">
                                <h3 className="text-xl font-black tracking-tight mb-2 text-white uppercase tracking-widest italic flex items-center gap-2">
                                    Elite <Zap className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                                </h3>
                                <p className="text-purple-400/60 text-sm italic">For power users</p>
                            </div>
                            <div className="mb-6">
                                <span className="text-6xl font-black tracking-tighter text-white">$60</span>
                                <span className="text-zinc-400 font-medium">/mo</span>
                            </div>
                            <div className="mb-6 p-3 rounded-xl bg-purple-500/10 border border-purple-500/20">
                                <p className="text-purple-400 text-sm font-medium flex items-center gap-2">
                                    <Check className="w-4 h-4" /> 25,000 SUs / MO
                                </p>
                            </div>
                            <div className="flex-grow">
                                <ul className="space-y-3 mb-8 text-sm text-zinc-300">
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-purple-400 shrink-0" />
                                        <span className="font-bold text-white">Everything in Pro</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-purple-400 shrink-0" />
                                        <span>Context-Engine (RLM)</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-purple-400 shrink-0" />
                                        <span className="font-bold">Unlimited Projects</span>
                                    </li>
                                </ul>
                            </div>
                            <CheckoutButton
                                variantId={process.env.LEMONSQUEEZY_VARIANT_ID_ELITE!}
                                label="GO ELITE"
                                variant="purple"
                            />
                        </div>

                        {/* High Tech - Custom */}
                        <div className="relative p-8 rounded-3xl border border-white/10 bg-zinc-900/50 flex flex-col hover:border-white/20 transition-colors duration-300">
                            <div className="mb-6">
                                <h3 className="text-xl font-bold tracking-tight mb-2 flex items-center gap-2 text-white uppercase tracking-widest">High Tech</h3>
                                <p className="text-zinc-400 text-sm italic">For IP-Sensitive Enterprises</p>
                            </div>
                            <div className="mb-8 flex flex-col justify-center h-20">
                                <span className="text-4xl font-bold tracking-tighter text-white">Custom</span>
                                <span className="text-[10px] uppercase tracking-widest text-zinc-500 font-bold mt-1">ABSOLUTE CONTROL</span>
                            </div>
                            <div className="flex-grow">
                                <ul className="space-y-3 mb-8 text-sm text-zinc-400">
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-white shrink-0" />
                                        <span className="text-zinc-300">Airgap Mode (Ollama, Azure & Custom)</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-white shrink-0" />
                                        <span className="text-zinc-300">System Pulse</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-white shrink-0" />
                                        <span className="text-zinc-300">Fractal Memory</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <Check className="w-4 h-4 text-white shrink-0" />
                                        <span className="text-zinc-300">Decision Database</span>
                                    </li>
                                </ul>
                            </div>
                            <a
                                href="mailto:hq@sidelith.com"
                                className="w-full h-12 rounded-full border border-white/10 flex items-center justify-center font-medium hover:bg-white hover:text-black hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 mt-auto"
                            >
                                Contact Sales →
                            </a>
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
                                    <div className="text-3xl font-black tracking-tighter text-cyan-400 font-mono">250</div>
                                    <div className="text-[10px] uppercase tracking-widest text-zinc-500 font-bold">Extra SUs</div>
                                </div>
                                <CheckoutButton
                                    variantId={process.env.LEMONSQUEEZY_VARIANT_ID_REFILL!}
                                    label="REFILL SUs"
                                    className="ml-4 h-12 px-6"
                                />
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
