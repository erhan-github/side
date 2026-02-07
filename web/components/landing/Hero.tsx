import { ArrowRight } from "lucide-react";

export function Hero() {
    return (
        <section className="w-full max-w-5xl px-6 flex flex-col items-center text-center z-10 pt-40 pb-20">
            <h1 className="text-hero mb-8 bg-gradient-to-b from-white to-white/60 bg-clip-text text-transparent animate-in fade-in slide-in-from-bottom-8 duration-1000 fill-mode-both leading-[1.2] pb-1">
                Intelligence that Remembers.
            </h1>

            <p className="text-xl md:text-2xl text-white/50 max-w-3xl mb-12 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-200 fill-mode-both leading-relaxed font-light">
                Sidelith is the <span className="text-white font-medium">deterministic memory substrate</span> for AI agents. <br />
                Curing digital amnesia with fractal ontology and 100% local persistence.
            </p>

            <div className="flex flex-col items-center gap-6 animate-in fade-in slide-in-from-bottom-16 duration-1000 delay-300 fill-mode-both">
                <a href="#install-widget" className="group flex items-center gap-2 px-8 py-4 rounded-full bg-white text-black font-bold hover:bg-neon hover:text-black transition-all shadow-[0_0_40px_rgba(255,255,255,0.1)] hover:shadow-[0_0_60px_rgba(0,255,157,0.3)]">
                    The Developer's Shortcut <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                </a>
            </div>
        </section>
    );
}
