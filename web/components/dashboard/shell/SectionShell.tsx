import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface SectionShellProps {
    title: string;
    description?: string;
    icon?: LucideIcon;
    children: React.ReactNode;
    className?: string;
    headerAction?: React.ReactNode;
}

export function SectionShell({ title, description, icon: Icon, children, className, headerAction }: SectionShellProps) {
    return (
        <div className={cn("bg-[#0c0c0e] border border-white/10 rounded-xl p-6", className)}>
            <div className="flex justify-between items-start mb-6">
                <div>
                    <h3 className="text-white font-medium flex items-center gap-2">
                        {Icon && <Icon className="w-5 h-5 text-zinc-400" />}
                        {title}
                    </h3>
                    {description && (
                        <p className="text-xs text-zinc-500 mt-1">{description}</p>
                    )}
                </div>
                {headerAction}
            </div>
            {children}
        </div>
    );
}
