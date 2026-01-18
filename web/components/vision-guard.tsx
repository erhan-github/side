import { Target, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface VisionStatus {
    alignmentScore: number;
    activeGoals: number;
    driftsDetected: number;
    status: 'OPTIMAL' | 'DRIFTING' | 'CRITICAL';
}

export function VisionGuard({ status }: { status: VisionStatus }) {
    return (
        <div className="p-6 rounded-xl border border-white/10 bg-zinc-900/40 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-2">
                    <Target className="w-4 h-4 text-purple-400" />
                    <h3 className="font-bold tracking-tight uppercase text-xs tracking-[0.2em]">Vision Guard</h3>
                </div>
                <div className={cn(
                    "px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-tighter border",
                    status.status === 'OPTIMAL' && "bg-green-500/10 text-green-500 border-green-500/20",
                    status.status === 'DRIFTING' && "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
                    status.status === 'CRITICAL' && "bg-red-500/10 text-red-500 border-red-500/20"
                )}>
                    {status.status}
                </div>
            </div>

            <div className="mb-8">
                <div className="flex justify-between items-end mb-2">
                    <span className="text-zinc-500 text-[10px] font-mono uppercase">Alignment Accuracy</span>
                    <span className="text-xl font-bold font-mono">{status.alignmentScore}%</span>
                </div>
                <div className="h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
                    <div
                        className={cn(
                            "h-full transition-all duration-1000",
                            status.status === 'OPTIMAL' && "bg-green-500",
                            status.status === 'DRIFTING' && "bg-yellow-500",
                            status.status === 'CRITICAL' && "bg-red-500"
                        )}
                        style={{ width: `${status.alignmentScore}%` }}
                    />
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded-lg bg-white/[0.03] border border-white/5">
                    <div className="text-zinc-500 text-[10px] font-mono mb-1 uppercase tracking-tighter">Active Goals</div>
                    <div className="text-lg font-bold">{status.activeGoals}</div>
                </div>
                <div className="p-3 rounded-lg bg-white/[0.03] border border-white/5">
                    <div className="text-zinc-500 text-[10px] font-mono mb-1 uppercase tracking-tighter">Vision Drifts</div>
                    <div className={cn(
                        "text-lg font-bold",
                        status.driftsDetected > 0 ? "text-yellow-500" : "text-zinc-400"
                    )}>{status.driftsDetected}</div>
                </div>
            </div>

            {status.driftsDetected > 0 && (
                <div className="mt-6 flex gap-3 p-3 rounded-lg bg-yellow-500/5 border border-yellow-500/10 items-start">
                    <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5" />
                    <p className="text-[11px] text-yellow-500/80 leading-relaxed font-medium">
                        Warning: You are attempting to build features previously rejected as &quot;non-strategic&quot;. CSO.ai is blocking redundant effort.
                    </p>
                </div>
            )}
        </div>
    );
}
