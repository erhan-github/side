export function LandingFooter() {
    return (
        <footer className="w-full border-t border-white/5 py-12 relative z-10">
            <div className="max-w-6xl mx-auto px-6 flex justify-between items-center text-xs text-white/30 font-mono">
                <div className="flex gap-4">
                    <span className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-emerald-500/50" /> All Systems Operational</span>
                    <span>Memory: 148MB Used</span>
                </div>
                <div>
                    "Intelligence means being able to survive the user's mistakes."
                </div>
            </div>
        </footer>
    );
}
