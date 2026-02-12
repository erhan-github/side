"use client";

import Link from "next/link";
import Image from "next/image";
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
        sm: 20,
        md: 24,
        lg: 40
    };

    return (
        <Link href="/" className={cn("flex items-center gap-3 group", className)}>
            {showIcon && (
                <div className="relative flex items-center justify-center">
                    <Image 
                        src="/assets/sidelith_small_icon.png" 
                        alt="Sidelith" 
                        width={iconSizes[size]} 
                        height={iconSizes[size]}
                        className="group-hover:rotate-12 transition-transform duration-500"
                    />
                </div>
            )}
            <div className={cn(
                "font-bold tracking-tighter bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent group-hover:from-white group-hover:to-white transition-all duration-300",
                sizeClasses[size]
            )}>
                Sidelith
            </div>
        </Link>
    );
}
