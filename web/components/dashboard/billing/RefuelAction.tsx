"use client";

import { Zap } from "lucide-react";

export function RefuelAction() {
    return (
        <button
            onClick={() => alert("Refueling Initiated. (Stub)")}
            className="w-full bg-white text-black hover:bg-zinc-200 font-medium py-2 rounded-lg transition-colors flex items-center justify-center gap-2 text-sm"
        >
            <Zap className="w-4 h-4 text-black" /> Instant Refuel
        </button>
    );
}
