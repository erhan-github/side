import { AlertTriangle, FileText, Code, Shield } from "lucide-react";

interface ForensicIssue {
    type: string; // 'STALE_DOCS', 'COMPLEXITY', 'NOISE', etc.
    severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    message: string;
    action: string;
}

export function SanityAlert({ issue }: { issue: ForensicIssue }) {
    const isCritical = issue.severity === 'CRITICAL';

    return (
        <div className={`
            p-4 rounded-lg border backdrop-blur-sm flex gap-4 items-start transition-all hover:bg-white/[0.02]
            ${isCritical
                ? 'border-red-500/20 bg-red-500/5'
                : 'border-white/5 bg-zinc-900/30'}
        `}>
            {/* Icon Column */}
            <div className={`
                mt-0.5
                ${isCritical ? 'text-red-400' : 'text-zinc-500'}
            `}>
                {issue.type === 'STALE_DOCS' && <FileText className="w-4 h-4" />}
                {issue.type === 'COMPLEXITY' && <Code className="w-4 h-4" />}
                {issue.type.includes('PURITY') && <Shield className="w-4 h-4" />}
                {!['STALE_DOCS', 'COMPLEXITY'].includes(issue.type) && !issue.type.includes('PURITY') && <AlertTriangle className="w-4 h-4" />}
            </div>

            {/* Content Column */}
            <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                    <span className={`
                        text-[10px] font-bold uppercase tracking-wider
                        ${isCritical ? 'text-red-500' : 'text-zinc-500'}
                    `}>
                        {issue.type.replace('_', ' ')}
                    </span>
                    {/* Silent Severity Indicator */}
                    <div className="flex gap-0.5">
                        <div className={`w-1 h-3 rounded-full ${['MEDIUM', 'HIGH', 'CRITICAL'].includes(issue.severity) ? 'bg-zinc-700' : 'bg-zinc-800'}`} />
                        <div className={`w-1 h-3 rounded-full ${['HIGH', 'CRITICAL'].includes(issue.severity) ? 'bg-zinc-600' : 'bg-zinc-800'}`} />
                        <div className={`w-1 h-3 rounded-full ${issue.severity === 'CRITICAL' ? 'bg-red-500' : 'bg-zinc-800'}`} />
                    </div>
                </div>

                <p className="text-sm text-zinc-400 leading-snug mb-3 font-light">
                    {issue.message}
                </p>

                {/* Recommendation (Silent Guidance) */}
                <div className="flex items-center gap-2 text-[11px]">
                    <span className="text-zinc-600 font-mono">SUGGESTION:</span>
                    <span className="text-zinc-300 font-mono border-b border-white/10 pb-0.5">
                        {issue.action}
                    </span>
                </div>
            </div>
        </div>
    );
}
