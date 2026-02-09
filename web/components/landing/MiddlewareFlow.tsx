import { ArrowRight, Bot, Database, User } from "lucide-react";

export function MiddlewareFlow() {
    return (
        <section className="py-16 w-full max-w-5xl mx-auto px-6">
            <div className="text-center mb-16">
                <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                    How Sidelith Works
                </h2>
                <p className="text-zinc-400 text-lg md:text-xl font-light max-w-2xl mx-auto">
                    Sits between you and AI to inject your project's context automatically.
                </p>
            </div>

            <div className="relative p-12 rounded-[32px] border border-white/10 bg-white/[0.02] overflow-hidden">
                {/* Simplified Linear Flow */}
                <div className="flex flex-col md:flex-row items-center justify-center gap-12 relative z-10">

                    {/* Step 1: You */}
                    <div className="flex flex-col items-center gap-5 text-center">
                        <div className="w-24 h-24 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center shadow-xl backdrop-blur-sm">
                            <User className="text-white w-10 h-10" />
                        </div>
                        <div>
                            <h3 className="text-white font-bold text-lg mb-1">You</h3>
                            <p className="text-zinc-400 text-sm font-medium">Ask a question</p>
                        </div>
                    </div>

                    {/* Arrow 1 */}
                    <div className="hidden md:flex flex-col items-center">
                        <ArrowRight className="text-white/20 w-8 h-8" />
                    </div>

                    {/* Step 2: Sidelith (Center) */}
                    <div className="flex flex-col items-center gap-5 text-center relative">
                        {/* Glow Effect */}
                        <div className="absolute inset-0 bg-blue-500/20 blur-3xl rounded-full" />

                        <div className="w-28 h-28 rounded-3xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/30 flex items-center justify-center shadow-2xl backdrop-blur-md relative z-10">
                            <Database className="text-blue-400 w-12 h-12" />
                        </div>
                        <div className="relative z-10">
                            <h3 className="text-white font-bold text-lg mb-1">Sidelith</h3>
                            <p className="text-blue-300/80 text-sm font-medium">Injects Context</p>
                        </div>
                    </div>

                    {/* Arrow 2 */}
                    <div className="hidden md:flex flex-col items-center">
                        <ArrowRight className="text-white/20 w-8 h-8" />
                    </div>

                    {/* Step 3: AI */}
                    <div className="flex flex-col items-center gap-5 text-center">
                        <div className="w-24 h-24 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center shadow-xl backdrop-blur-sm">
                            <Bot className="text-purple-400 w-10 h-10" />
                        </div>
                        <div>
                            <h3 className="text-white font-bold text-lg mb-1">AI</h3>
                            <p className="text-zinc-400 text-sm font-medium">Better Response</p>
                        </div>
                    </div>

                </div>
            </div>
        </section>
    );
}
