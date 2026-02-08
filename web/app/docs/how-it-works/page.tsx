import { Header } from "@/components/Header";
import { LandingFooter } from "@/components/landing/LandingFooter";

export const metadata = {
    title: "How It Works | Sidelith",
    description: "Understanding fractal indexing and local-first architecture.",
};

export default function HowItWorksPage() {
    return (
        <div className="min-h-screen bg-[#050505] text-white font-sans">
            <Header />

            <div className="max-w-7xl mx-auto px-6 pt-32 pb-20">
                <div className="max-w-3xl">
                    <div className="mb-16">
                        <h1 className="text-4xl md:text-5xl font-bold mb-6 font-heading">
                            How It Works
                        </h1>
                        <p className="text-xl text-zinc-400 leading-relaxed mb-12">
                            Sidelith builds a persistent, fractal index of your codebase. Unlike standard RAG which chunks text blindly, we understand your code's abstract syntax tree (AST).
                        </p>

                        <div className="grid grid-cols-1 gap-6">
                            {[
                                {
                                    title: "Fractal Indexing",
                                    desc: "We extract structural signals using Tree-sitter to create a map of your entire project. This allows Sidelith to understand the relationships between files, classes, and functions."
                                },
                                {
                                    title: "Local-First",
                                    desc: "Your code never leaves your machine. The index resides locally in `.side/` directory within your project root. This ensures zero latency and maximum privacy."
                                },
                                {
                                    title: "IDE Integration",
                                    desc: "We inject this context directly into Cursor, VS Code, and Claude Desktop via the Model Context Protocol (MCP). Your AI assistant gains 'eyes' into your actual project structure."
                                }
                            ].map((item) => (
                                <div key={item.title} className="p-8 rounded-xl bg-white/[0.02] border border-white/10">
                                    <h3 className="text-xl font-bold text-white mb-3 font-heading">{item.title}</h3>
                                    <p className="text-zinc-400 leading-relaxed">{item.desc}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <LandingFooter />
        </div>
    );
}
