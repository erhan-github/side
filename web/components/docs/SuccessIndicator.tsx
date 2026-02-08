"use client";

import { CheckCircle2 } from "lucide-react";

interface SuccessIndicatorProps {
    title: string;
    description: string;
}

export function SuccessIndicator({ title, description }: SuccessIndicatorProps) {
    return (
        <div className="my-8 p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20 flex gap-4">
            <div className="shrink-0 pt-0.5">
                <CheckCircle2 size={20} className="text-emerald-500" />
            </div>
            <div>
                <h4 className="text-sm font-bold text-emerald-400 mb-1">{title}</h4>
                <p className="text-sm text-zinc-400 leading-relaxed">{description}</p>
            </div>
        </div>
    );
}
