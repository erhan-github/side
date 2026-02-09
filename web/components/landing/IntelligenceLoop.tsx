import { ArrowRight, ArrowDown } from "lucide-react";

export function IntelligenceLoop() {
    return (
        <section className="w-full max-w-7xl mx-auto px-6 py-16">

            {/* Title */}
            <div className="text-center mb-16">
                <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                    How Sidelith Works
                </h2>
                <p className="text-white/60 text-xl max-w-2xl mx-auto">
                    A straight line to better code.
                </p>
            </div>

            {/* Linear Flow Container */}
            <div className="flex flex-col md:flex-row items-center justify-between gap-8 relative">

                {/* Connecting Line (Desktop) */}
                <div className="hidden md:block absolute top-[2rem] left-0 w-full h-1 bg-zinc-800 -z-10" />

                {/* Step 1 */}
                <div className="flex flex-col items-center text-center max-w-xs relative w-full md:w-auto">
                    <div className="w-16 h-16 rounded-xl bg-zinc-900 border border-zinc-700 flex items-center justify-center text-xl font-bold text-white mb-6 z-10 shadow-xl">
                        01
                    </div>
                    <h3 className="text-white font-bold text-lg mb-2">Intent Inference</h3>
                    <p className="text-zinc-400 text-sm leading-relaxed">
                        Understands what you want to accomplish, not just the code you typed.
                    </p>
                </div>

                {/* Arrow 1 (Desktop) / (Mobile) */}
                <div className="hidden md:block text-zinc-600">
                    <ArrowRight className="w-6 h-6" />
                </div>
                <div className="md:hidden text-zinc-600 my-2">
                    <ArrowDown className="w-6 h-6" />
                </div>

                {/* Step 2 */}
                <div className="flex flex-col items-center text-center max-w-xs relative w-full md:w-auto">
                    <div className="w-16 h-16 rounded-xl bg-zinc-900 border border-zinc-700 flex items-center justify-center text-xl font-bold text-white mb-6 z-10 shadow-xl">
                        02
                    </div>
                    <h3 className="text-white font-bold text-lg mb-2">Architectural Mapping</h3>
                    <p className="text-zinc-400 text-sm leading-relaxed">
                        Finds existing patterns and constraints in your project.
                    </p>
                </div>

                {/* Arrow 2 */}
                <div className="hidden md:block text-zinc-600">
                    <ArrowRight className="w-6 h-6" />
                </div>
                <div className="md:hidden text-zinc-600 my-2">
                    <ArrowDown className="w-6 h-6" />
                </div>

                {/* Step 3 */}
                <div className="flex flex-col items-center text-center max-w-xs relative w-full md:w-auto">
                    <div className="w-16 h-16 rounded-xl bg-zinc-900 border border-zinc-700 flex items-center justify-center text-xl font-bold text-white mb-6 z-10 shadow-xl">
                        03
                    </div>
                    <h3 className="text-white font-bold text-lg mb-2">Constrained Generation</h3>
                    <p className="text-zinc-400 text-sm leading-relaxed">
                        Generates code that fits your specific architecture strictly.
                    </p>
                </div>

                {/* Arrow 3 */}
                <div className="hidden md:block text-zinc-600">
                    <ArrowRight className="w-6 h-6" />
                </div>
                <div className="md:hidden text-zinc-600 my-2">
                    <ArrowDown className="w-6 h-6" />
                </div>

                {/* Step 4 */}
                <div className="flex flex-col items-center text-center max-w-xs relative w-full md:w-auto">
                    <div className="w-16 h-16 rounded-xl bg-emerald-900/20 border border-emerald-500/50 flex items-center justify-center text-xl font-bold text-emerald-400 mb-6 z-10 shadow-xl shadow-emerald-900/20">
                        04
                    </div>
                    <h3 className="text-white font-bold text-lg mb-2">Validation</h3>
                    <p className="text-zinc-400 text-sm leading-relaxed">
                        Ensures the fix works and updates the system of record.
                    </p>
                </div>

            </div>
        </section>
    );
}
