import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface PageHeaderProps {
    title: string;
    description: string;
    icon?: LucideIcon;
    iconColor?: string;
    action?: React.ReactNode;
}

export function PageHeader({ title, description, icon: Icon, iconColor = "text-white", action }: PageHeaderProps) {
    return (
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
            <div>
                <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight mb-2 flex items-center gap-3">
                    {Icon && <Icon className={cn("w-8 h-8", iconColor)} />}
                    {title}
                </h1>
                <p className="text-zinc-500 max-w-xl font-medium">
                    {description}
                </p>
            </div>
            {action && (
                <div>
                    {action}
                </div>
            )}
        </div>
    );
}
