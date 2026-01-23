import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
    label: string;
    value: React.ReactNode;
    icon?: LucideIcon;
    iconColor?: string;
    description?: React.ReactNode;
    trend?: {
        value: number; // percentage
        positive: boolean;
    };
    className?: string;
}

export function StatCard({ label, value, icon: Icon, iconColor = "text-zinc-400", description, className }: StatCardProps) {
    return (
        <div className={cn("bg-[#0c0c0e] border border-white/10 rounded-xl p-6", className)}>
            <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-zinc-900 flex items-center justify-center border border-white/5">
                    {Icon && <Icon className={cn("w-5 h-5", iconColor)} />}
                </div>
                <div>
                    <h3 className="text-white font-medium">{label}</h3>
                    {description && <div className="text-xs text-zinc-500">{description}</div>}
                </div>
            </div>
            <div className="text-3xl font-black font-mono text-white mb-1">
                {value}
            </div>
            {/* Trend could go here */}
        </div>
    );
}
