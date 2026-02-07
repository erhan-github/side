"use client";

import { Globe, Server, Power, Download } from "lucide-react";

// This component is mostly static but has "Export" button which needs client interaction.
// We keep it as a client component to isolate the button logic.
export function DataPrivacy() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Telemetry Control */}
            <div className="bg-[#0c0c0e] border border-white/10 rounded-xl p-6 flex flex-col justify-between">
                <div>
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-lg bg-zinc-900 flex items-center justify-center border border-white/5">
                            <Globe className="w-5 h-5 text-blue-400" />
                        </div>
                        <div>
                            <h3 className="text-white font-bold">Judicial Cloud Sync</h3>
                            <p className="text-xs text-zinc-500 font-medium">Data sent to Sidelith Registry</p>
                        </div>
                    </div>
                    <div className="text-3xl font-black font-mono text-white mb-1">100 <span className="text-zinc-500 text-lg uppercase tracking-tighter">%</span></div>
                    <div className="h-2 w-full bg-zinc-800 rounded-full mt-4 overflow-hidden border border-white/5">
                        <div className="h-full bg-blue-500 w-full" />
                    </div>
                </div>
                <div className="mt-6 pt-6 border-t border-white/5">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-zinc-400">Crash Reports</span>
                        <div className="flex items-center gap-2">
                            <span className="text-xs text-emerald-500">Disabled</span>
                            <Power className="w-4 h-4 text-emerald-500" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Local Storage */}
            <div className="bg-[#0c0c0e] border border-white/10 rounded-xl p-6 flex flex-col justify-between">
                <div>
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-lg bg-zinc-900 flex items-center justify-center border border-white/5">
                            <Server className="w-5 h-5 text-zinc-400" />
                        </div>
                        <div>
                            <h3 className="text-white font-medium">Local Intelligence</h3>
                            <p className="text-xs text-zinc-500">Stored on device (~/.side/data)</p>
                        </div>
                    </div>
                    <div className="text-3xl font-mono text-white mb-1">142 <span className="text-zinc-600 text-lg">MB</span></div>
                    <div className="flex gap-1 mt-4">
                        <div className="h-1 bg-purple-500 w-[60%] rounded-l-full" />
                        <div className="h-1 bg-blue-500 w-[30%]" />
                        <div className="h-1 bg-zinc-700 w-[10%] rounded-r-full" />
                    </div>
                    <div className="flex justify-between text-[10px] text-zinc-500 mt-2 font-mono uppercase">
                        <span className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-purple-500" /> Embeddings</span>
                        <span className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-blue-500" /> Context</span>
                        <span className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-zinc-700" /> Logs</span>
                    </div>
                </div>
                <div className="mt-6 pt-6 border-t border-white/5 flex gap-3">
                    <button
                        onClick={() => alert("Exporting local intelligence... (Stub)")}
                        className="flex-1 bg-white/5 hover:bg-white/10 text-white text-xs font-medium py-2 rounded border border-white/5 transition-colors flex items-center justify-center gap-2"
                    >
                        <Download className="w-3 h-3" /> Export
                    </button>
                </div>
            </div>
        </div>
    );
}
