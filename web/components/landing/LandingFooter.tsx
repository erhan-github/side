import { BrandLogo } from "@/components/ui/BrandLogo";

export function LandingFooter() {
    return (
        <footer className="w-full border-t border-white/5 py-12 relative z-10">
            <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-8 text-xs text-white/30 font-mono">
                <div className="flex flex-col gap-6">
                    <BrandLogo size="sm" />
                    <div className="flex gap-4">
                        <span className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-emerald-500/50" /> All Systems Operational</span>
                        <span>Memory: 148MB Used</span>
                    </div>
                </div>
                <div className="max-w-xs text-right opacity-50">
                    "Intelligence means being able to survive the user's mistakes."
                </div>
            </div>
        </footer>
    );
}
