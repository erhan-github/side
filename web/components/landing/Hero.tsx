import { ArrowRight } from "lucide-react";

export function Hero() {
    return (
        <section className="w-full max-w-7xl mx-auto px-6 pt-8 pb-16 z-10">
            <div className="max-w-4xl">
                <h1 className="text-5xl md:text-7xl font-extrabold mb-8 bg-gradient-to-br from-white to-white/80 bg-clip-text text-transparent animate-in fade-in slide-in-from-bottom-8 duration-1000 fill-mode-both leading-[1.05] tracking-tight pb-1">
                    AI coding tools that remember your architecture.
                </h1>

                <p className="text-xl md:text-2xl text-zinc-300 max-w-2xl mb-12 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-200 fill-mode-both leading-relaxed font-light">
                    Stop re-explaining your codebase every conversation. Sidelith gives Cursor and Claude <span className="text-white font-medium">Persistent Context</span>.
                </p>

                <div className="mb-12 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-200 fill-mode-both">
                    <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-sm font-medium">
                        <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        Developers save 8+ hours/week by not repeating context
                    </div>
                </div>

                <div className="flex flex-col sm:flex-row items-center gap-4 animate-in fade-in slide-in-from-bottom-16 duration-1000 delay-300 fill-mode-both">
                    <a href="#install-widget" className="group flex items-center justify-center gap-2 px-8 py-4 rounded-full bg-white text-black font-bold hover:bg-zinc-200 transition-all shadow-[0_0_20px_rgba(255,255,255,0.1)] hover:shadow-[0_0_40px_rgba(255,255,255,0.2)] w-full sm:w-auto">
                        Get Started for Free <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                    </a>
                    <a href="/docs" className="flex items-center justify-center gap-2 px-8 py-4 rounded-full border border-white/20 text-white font-bold hover:bg-white/5 hover:border-white/40 transition-all w-full sm:w-auto">
                        Docs
                    </a>
                </div>
            </div>
        </section>
    );
}
