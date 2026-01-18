import { Zap, Shield, AlertTriangle, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface PulseSignal {
    type: 'SHORTCUT' | 'MOAT' | 'RISK';
    content: string;
    timestamp: string;
}

export function PulseWidget({ signals }: { signals: PulseSignal[] }) {
    return (
        <div className="p-6 rounded-xl border border-white/10 bg-zinc-900/40 backdrop-blur-sm relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-16 bg-yellow-500/5 blur-3xl group-hover:bg-yellow-500/10 transition-all" />

            <div className="flex items-center justify-between mb-6 relative z-10">
                <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-yellow-400 animate-pulse" />
                    <h3 className="font-bold tracking-tight">THE PULSE</h3>
                </div>
                <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-widest">Live Signals</span>
            </div>

            <div className="space-y-4 relative z-10">
                {signals.length > 0 ? (
                    signals.map((signal, idx) => (
                        <div key={idx} className="flex gap-4 items-start group/item">
                            <div className={cn(
                                "mt-1 p-1.5 rounded-md",
                                signal.type === 'SHORTCUT' && "bg-blue-500/20 text-blue-400",
                                signal.type === 'MOAT' && "bg-green-500/20 text-green-400",
                                signal.type === 'RISK' && "bg-red-500/20 text-red-400"
                            )}>
                                {signal.type === 'SHORTCUT' && <Zap className="w-3 h-3" />}
                                {signal.type === 'MOAT' && <Shield className="w-3 h-3" />}
                                {signal.type === 'RISK' && <AlertTriangle className="w-3 h-3" />}
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 mb-0.5">
                                    <span className={cn(
                                        "text-[10px] font-bold uppercase tracking-wider",
                                        signal.type === 'SHORTCUT' && "text-blue-500",
                                        signal.type === 'MOAT' && "text-green-500",
                                        signal.type === 'RISK' && "text-red-500"
                                    )}>
                                        {signal.type}
                                    </span>
                                    <span className="text-[10px] text-zinc-600 font-mono">{signal.timestamp}</span>
                                </div>
                                <p className="text-sm text-zinc-300 leading-relaxed group-hover/item:text-white transition-colors">
                                    {signal.content}
                                </p>
                            </div>
                            <ChevronRight className="w-4 h-4 text-zinc-700 mt-2 opacity-0 group-hover/item:opacity-100 transition-all" />
                        </div>
                    ))
                ) : (
                    <div className="py-8 text-center text-zinc-600 italic text-sm">
                        Waiting for strategic breakthroughs...
                    </div>
                )}
            </div>

            <div className="mt-6 pt-4 border-t border-white/5 flex justify-between items-center relative z-10">
                <span className="text-[10px] text-zinc-500">v3 Precision Engine</span>
                <button className="text-[10px] font-bold text-zinc-400 hover:text-white transition-colors uppercase tracking-widest flex items-center gap-1">
                    View History <ChevronRight className="w-3 h-3" />
                </button>
            </div>
        </div>
    );
}
