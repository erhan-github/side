import { Zap } from "lucide-react";

export function PricingSection() {
    return (
        <section className="w-full max-w-6xl px-6 py-16 relative z-10">
            <div className="text-center mb-16">
                <h2 className="text-4xl md:text-5xl font-bold text-white mb-3">Scale for <span className="text-amber-500">Intelligence</span></h2>
                <p className="text-base text-white/50">Deterministic capacity for your semantic operations.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                {/* TRIAL - Small Card */}
                <div className="md:col-span-1 p-6 rounded-[28px] bg-[#0a0a0a] border border-white/5 hover:border-white/10 transition-all group">
                    <div className="text-[10px] font-mono text-white/30 tracking-widest uppercase mb-2">Hobby</div>
                    <div className="text-3xl font-bold text-white mb-1">$0</div>
                    <div className="text-[10px] font-mono text-white/40 mb-4">500 SUs / MO</div>
                    <p className="text-xs text-white/30 mb-6">Individual use and evaluation.</p>
                    <a href="#install-widget" className="block text-center py-2 px-4 rounded-xl border border-white/10 hover:border-white/20 text-xs font-bold text-white transition-colors uppercase tracking-widest">
                        Start Free
                    </a>
                </div>

                {/* PRO - Featured Card (Spans 2 columns) */}
                <div className="md:col-span-2 p-8 rounded-[28px] bg-gradient-to-br from-amber-500/[0.08] to-orange-500/[0.08] border border-amber-500/30 hover:border-amber-500/50 transition-all group relative overflow-hidden">
                    <div className="absolute top-4 right-4 px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500/40 text-[8px] font-mono text-amber-500 uppercase tracking-widest">
                        ⭐ Popular
                    </div>
                    <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/10 blur-[60px] rounded-full group-hover:bg-amber-500/20 transition-colors" />

                    <div className="relative z-10">
                        <div className="text-[10px] font-mono text-amber-500/60 tracking-widest uppercase mb-2">Pro</div>
                        <div className="text-4xl font-bold text-white mb-1">$20</div>
                        <div className="text-sm font-mono text-white/60 mb-6">5,000 SUs / MO</div>
                        <p className="text-sm text-white/60 mb-6">For professional developers delivering code daily.</p>

                        <div className="mb-6">
                            <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                <div className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full w-3/4 group-hover:w-full transition-all duration-1000" />
                            </div>
                            <div className="text-[8px] font-mono text-amber-500/60 mt-2 uppercase tracking-widest">5K SU Capacity</div>
                        </div>

                        <a href="#install-widget" className="block text-center py-3 px-6 rounded-xl bg-amber-500/20 border border-amber-500/40 hover:bg-amber-500/30 text-sm font-bold text-white transition-colors uppercase tracking-widest">
                            Get Started
                        </a>
                    </div>
                </div>

                {/* ELITE - Small Card */}
                <div className="md:col-span-1 p-6 rounded-[28px] bg-[#0a0a0a] border border-white/5 hover:border-purple-500/30 transition-all group">
                    <div className="text-[10px] font-mono text-white/30 tracking-widest uppercase mb-2">Elite</div>
                    <div className="text-3xl font-bold text-white mb-1">$60</div>
                    <div className="text-[10px] font-mono text-white/40 mb-4">25,000 SUs / MO</div>
                    <p className="text-xs text-white/30 mb-6">For power users and small teams.</p>
                    <a href="#install-widget" className="block text-center py-2 px-4 rounded-xl border border-white/10 hover:border-purple-500/30 text-xs font-bold text-white transition-colors uppercase tracking-widest">
                        Upgrade
                    </a>
                </div>
            </div>

            {/* Enterprise & Airgapped - 2 Column Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Enterprise */}
                <div className="p-8 rounded-[28px] bg-gradient-to-br from-[#0a0a0a] to-[#1a1a1a] border border-white/10 hover:border-blue-500/30 transition-all group relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 blur-[50px] rounded-full group-hover:bg-blue-500/10 transition-colors" />
                    <div className="relative z-10 flex flex-col h-full justify-between">
                        <div>
                            <div className="text-[10px] font-mono text-blue-400 tracking-widest uppercase mb-2">Enterprise</div>
                            <h3 className="text-2xl font-bold text-white mb-2">Cloud Teams</h3>
                            <p className="text-white/50 text-sm mb-6">SSO, Shared Context Pools, and Team Analytics.</p>
                            <div className="flex flex-wrap gap-2 mb-6">
                                <span className="text-[10px] px-2 py-1 rounded bg-white/5 border border-white/10 text-white/60">SAML SSO</span>
                                <span className="text-[10px] px-2 py-1 rounded bg-white/5 border border-white/10 text-white/60">Team Pools</span>
                                <span className="text-[10px] px-2 py-1 rounded bg-white/5 border border-white/10 text-white/60">Audit API</span>
                            </div>
                        </div>
                        <a href="mailto:sales@sidelith.com" className="block text-center py-3 px-6 rounded-xl border border-white/10 hover:bg-blue-500/10 hover:border-blue-500/30 text-sm font-bold text-white transition-colors uppercase tracking-widest">
                            Contact Sales
                        </a>
                    </div>
                </div>

                {/* Airgapped */}
                <div className="p-8 rounded-[28px] bg-gradient-to-br from-slate-900 to-slate-800 border border-white/10 hover:border-emerald-500/30 transition-all group relative overflow-hidden">
                    <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-5 mix-blend-overlay" />
                    <div className="relative z-10 flex flex-col h-full justify-between">
                        <div>
                            <div className="text-[10px] font-mono text-emerald-400 tracking-widest uppercase mb-2">Airgapped</div>
                            <h3 className="text-2xl font-bold text-white mb-2">On-Premise</h3>
                            <p className="text-white/50 text-sm mb-6">Zero-egress deployment for regulated industries.</p>
                            <div className="flex flex-wrap gap-2 mb-6">
                                <span className="text-[10px] px-2 py-1 rounded bg-white/5 border border-white/10 text-white/60">BYOK LLM</span>
                                <span className="text-[10px] px-2 py-1 rounded bg-white/5 border border-white/10 text-white/60">No Cloud Sync</span>
                                <span className="text-[10px] px-2 py-1 rounded bg-white/5 border border-white/10 text-white/60">FIPS/ITAR</span>
                            </div>
                        </div>
                        <a href="mailto:enterprise@sidelith.com" className="block text-center py-3 px-6 rounded-xl bg-white/5 border border-white/10 hover:bg-emerald-500/10 hover:border-emerald-500/30 text-sm font-bold text-white transition-colors uppercase tracking-widest">
                            Talk to Engineering
                        </a>
                    </div>
                </div>
            </div>

            {/* Add-on: Structural Refills */}
            <div className="mt-12 p-6 rounded-2xl border border-white/5 bg-white/[0.01] flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="flex items-center gap-4">
                    <div className="p-3 rounded-xl bg-orange-500/10 border border-orange-500/20">
                        <Zap className="w-6 h-6 text-orange-400" />
                    </div>
                    <div>
                        <h4 className="text-sm font-bold text-white uppercase tracking-wider">Structural Refills</h4>
                        <p className="text-xs text-white/40 max-w-sm">Ran out of throughput? Add capacity incrementally to your Account. Credits are applied instantly.</p>
                    </div>
                </div>
                <div className="flex items-center gap-8 pr-4">
                    <div className="text-right">
                        <div className="text-2xl font-bold text-white">$10</div>
                        <div className="text-[10px] text-white/40 uppercase tracking-wider">2,500 SUs</div>
                    </div>
                </div>
            </div>
        </section>
    );
}
