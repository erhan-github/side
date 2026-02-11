"use client";

import Link from "next/link";
import { cn } from "@/lib/utils";

interface BrandLogoProps {
    className?: string;
    showIcon?: boolean;
    size?: "sm" | "md" | "lg";
}

export function BrandLogo({ className, showIcon = true, size = "md" }: BrandLogoProps) {
    const sizeClasses = {
        sm: "text-lg",
        md: "text-2xl",
        lg: "text-4xl"
    };

    const iconSizes = {
        sm: "w-4 h-4",
        md: "w-5 h-5",
        lg: "w-8 h-8"
    };

    return (
        <Link href="/" className={cn("flex items-center gap-2.5 group", className)}>
            {showIcon && (
                <div className={cn(
                    "bg-white rounded-sm group-hover:rotate-90 transition-transform duration-500",
                    iconSizes[size]
                )} />
            )}
            <div className={cn(
                "font-bold tracking-tight bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent group-hover:from-emerald-400 group-hover:to-blue-400 transition-all duration-300",
                sizeClasses[size]
            )}>
                Sidelith
            </div>
        </Link>
    );
}
