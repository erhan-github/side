import { ArrowRight, Bot, Database, User } from "lucide-react";

export function MiddlewareFlow() {
    return (
        <section className="section-spacing w-full max-w-5xl mx-auto px-6">
            <div className="text-center mb-16">
                <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
                    How Sidelith Works
                </h2>
                <p className="text-white/60 text-lg md:text-xl font-light max-w-2xl mx-auto">
                    Sits between you and AI to inject your project's context automatically.
                </p>
            </div>

            <div className="relative p-12 rounded-[32px] border border-white/10 bg-white/[0.02] overflow-hidden">
                {/* Simplified Linear Flow */}
                <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-12 relative z-10">

                    {/* Step 1: You */}
                    <div className="flex flex-col items-center gap-4 text-center">
                        <div className="w-20 h-20 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center shadow-xl backdrop-blur-sm">
                            <User className="text-white w-10 h-10" />
                        </div>
                        <div>
                            <h3 className="text-white font-bold text-lg">You</h3>
                            <p className="text-white/40 text-sm">Ask a question</p>
                        </div>
                    </div>

                    {/* Arrow 1 */}
                    <div className="hidden md:flex flex-col items-center">
                        <ArrowRight className="text-white/20 w-8 h-8" />
                    </div>

                    {/* Step 2: Sidelith (Center) */}
                    <div className="flex flex-col items-center gap-4 text-center relative">
                        {/* Glow Effect */}
                        <div className="absolute inset-0 bg-blue-500/20 blur-3xl rounded-full" />

                        <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/30 flex items-center justify-center shadow-2xl backdrop-blur-md relative z-10">
                            <Database className="text-blue-400 w-12 h-12" />
                        </div>
                        <div className="relative z-10">
                            <h3 className="text-white font-bold text-lg">Sidelith</h3>
                            <p className="text-blue-200/60 text-sm">Injects Context</p>
                        </div>
                    </div>

                    {/* Arrow 2 */}
                    <div className="hidden md:flex flex-col items-center">
                        <ArrowRight className="text-white/20 w-8 h-8" />
                    </div>

                    {/* Step 3: AI */}
                    <div className="flex flex-col items-center gap-4 text-center">
                        <div className="w-20 h-20 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center shadow-xl backdrop-blur-sm">
                            <Bot className="text-purple-400 w-10 h-10" />
                        </div>
                        <div>
                            <h3 className="text-white font-bold text-lg">AI</h3>
                            <p className="text-white/40 text-sm">Better Response</p>
                        </div>
                    </div>

                </div>
            </div>
        </section>
    );
}
