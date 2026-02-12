"use client";

import { useState } from "react";
import { generateApiKey } from "@/app/actions/api-keys";
import { Copy, Check, RefreshCw, Key } from "lucide-react";
import { SectionShell } from "@/components/dashboard/shell/SectionShell";

interface ApiKeySectionProps {
    initialKey: string | null;
}

export function ApiKeySection({ initialKey }: ApiKeySectionProps) {
    const [hint, setHint] = useState<string | null>(initialKey && initialKey.includes(':') ? initialKey.split(':')[1] : null);
    const [secret, setSecret] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [copied, setCopied] = useState(false);
    const [showSuccess, setShowSuccess] = useState(false);

    const handleGenerate = async () => {
        setIsLoading(true);
        setShowSuccess(false);
        try {
            const result = await generateApiKey();
            setSecret(result.secret);
            setHint(result.hint);
            setShowSuccess(true);
        } catch (error) {
            console.error("Failed to generate key:", error);
            alert("Failed to generate API key. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const displayValue = secret || hint || "Not Generated";
    const isSecretOnly = !!secret;

    const handleCopy = () => {
        if (!displayValue || displayValue === "Not Generated") return;
        navigator.clipboard.writeText(isSecretOnly ? secret : displayValue);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <SectionShell
            title="Security Keys"
            icon={Key}
        >
            <div className="space-y-6">
                <p className="text-xs text-zinc-500">
                    Your API key is used to connect local CLI and IDE extensions to your Sidelith account.
                    <span className="text-amber-500/80"> We only store a hash of your key; it cannot be recovered if lost.</span>
                </p>

                <div className="relative group">
                    <div className={`w-full bg-black border rounded-lg p-3 font-mono text-xs break-all pr-12 min-h-[42px] flex items-center ${isSecretOnly ? 'border-emerald-500/50 bg-emerald-500/5' : 'border-white/5 text-white/50'}`}>
                        {displayValue === "Not Generated" ? (
                            <span>Not Generated</span>
                        ) : (
                            <span className={isSecretOnly ? "text-emerald-400 font-bold" : "text-white"}>{displayValue}</span>
                        )}
                    </div>

                    {(secret || hint) && (
                        <button
                            onClick={handleCopy}
                            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 hover:bg-white/5 rounded-md transition-colors text-zinc-400 hover:text-white"
                            title="Copy to clipboard"
                        >
                            {copied ? <Check size={16} className="text-emerald-500" /> : <Copy size={16} />}
                        </button>
                    )}
                </div>

                {showSuccess && (
                    <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3">
                        <p className="text-[10px] text-emerald-400 font-medium uppercase tracking-tight">
                            Key Generated Successfully
                        </p>
                        <p className="text-[10px] text-emerald-500/70 mt-1">
                            Copy this key now. You will not be able to see it again.
                        </p>
                    </div>
                )}

                <button
                    onClick={handleGenerate}
                    disabled={isLoading}
                    className="w-full py-3 bg-white hover:bg-zinc-200 disabled:bg-zinc-800 disabled:text-zinc-600 text-black rounded-lg text-xs font-bold uppercase tracking-widest transition-all flex items-center justify-center gap-2"
                >
                    {isLoading ? (
                        <>
                            <RefreshCw size={14} className="animate-spin" />
                            Generating...
                        </>
                    ) : (
                        <>
                            <RefreshCw size={14} />
                            {(secret || hint) ? "Rotate API Key" : "Generate API Key"}
                        </>
                    )}
                </button>

                {(secret || hint) && (
                    <p className="text-[10px] text-amber-500/50 text-center font-medium uppercase tracking-tighter">
                        Warning: Rotating your key will invalidate existing CLI sessions.
                    </p>
                )}
            </div>
        </SectionShell>
    );
}
