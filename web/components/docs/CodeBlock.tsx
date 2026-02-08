"use client";

import { useState } from "react";
import { Copy, Check } from "lucide-react";

interface CodeBlockProps {
    code: string;
    language?: string;
    showPrompt?: boolean;
}

export function CodeBlock({ code, language = "bash", showPrompt = true }: CodeBlockProps) {
    const [copied, setCopied] = useState(false);

    const copyToClipboard = async () => {
        await navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="relative group rounded-xl overflow-hidden bg-black border border-white/20 my-6 shadow-inner transition-all hover:border-emerald-500/30">
            <div className="absolute z-10" style={{ top: "0.75rem", right: "0.75rem" }}>
                <button
                    onClick={copyToClipboard}
                    className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-all text-white/40 hover:text-white"
                    aria-label="Copy code"
                >
                    {copied ? <Check size={16} className="text-emerald-500" /> : <Copy size={16} />}
                </button>
            </div>

            <div className="p-5 overflow-x-auto font-mono text-base leading-relaxed">
                <pre className="text-white">
                    <code className="flex">
                        {showPrompt && (
                            <span className="text-white/30 mr-4">$</span>
                        )}
                        <span className={language === "bash" ? "text-emerald-400 font-bold tracking-tight" : ""}>{code}</span>
                    </code>
                </pre>
            </div>
        </div>
    );
}
