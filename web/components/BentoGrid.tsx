"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface BentoCardProps {
    title: string;
    description: string;
    graphic: ReactNode;
    className?: string;
    titleClass?: string;
}

export function BentoGrid({ children }: { children: ReactNode }) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-7xl mx-auto px-6">
            {children}
        </div>
    );
}

export function BentoCard({ title, description, graphic, className, titleClass }: BentoCardProps) {
    return (
        <motion.div
            whileHover={{ y: -5 }}
            className={cn(
                "group relative overflow-hidden rounded-xl border border-white/10 bg-white/[0.02] p-8 hover:border-white/20 transition-colors",
                className
            )}
        >
            <div className="absolute inset-0 bg-gradient-to-br from-white/[0.05] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

            <div className="relative z-10 flex flex-col h-full">
                <div className="mb-6 flex-grow flex items-center justify-center">
                    {graphic}
                </div>
                <div className="space-y-3">
                    <h3 className={cn("text-2xl font-bold text-white font-heading tracking-tight", titleClass)}>{title}</h3>
                    <p className="text-base text-zinc-300 leading-relaxed font-medium">{description}</p>
                </div>
            </div>
        </motion.div>
    );
}
