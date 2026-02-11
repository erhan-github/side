"use client";

import { Zap, Construction } from "lucide-react";

export default function AddonsPage() {
    return (
        <div className="p-4 md:p-8 max-w-[1600px] mx-auto min-h-screen flex flex-col items-center justify-center gap-6">
            <div className="w-16 h-16 bg-cyan-500/10 rounded-full flex items-center justify-center mb-4">
                <Zap className="w-8 h-8 text-cyan-500" />
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight text-center">
                Add-ons
            </h1>
            <p className="text-zinc-500 text-center max-w-md">
                Additional features and integrations coming soon.
            </p>
            <div className="flex items-center gap-2 text-zinc-600 text-xs uppercase tracking-[0.2em] font-black italic">
                <Construction className="w-4 h-4" /> Under Construction
            </div>
        </div>
    );
}
