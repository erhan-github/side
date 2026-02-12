"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

const ROLES = [
    "Context Layer",
    "Architecture Memory",
    "Senior Engineer",
    "Tech Lead",
    "System of Record"
];

interface RotatingRoleProps {
    className?: string;
    prefix?: string;
    suffix?: string;
}

export function RotatingRole({ className, prefix = "The ", suffix = " for your architecture." }: RotatingRoleProps) {
    const [index, setIndex] = useState(0);
    const [fade, setFade] = useState(true);

    useEffect(() => {
        const interval = setInterval(() => {
            setFade(false); // Start fade out
            setTimeout(() => {
                setIndex((prev) => (prev + 1) % ROLES.length);
                setFade(true); // Fade in
            }, 300); // Wait for fade out
        }, 3000);

        return () => clearInterval(interval);
    }, []);

    return (
        <p className={cn("transition-opacity duration-300", className)}>
            {prefix}
            <span className={cn("font-medium transition-opacity duration-300", fade ? "opacity-100" : "opacity-0")}>
                {ROLES[index]}
            </span>
            {suffix}
        </p>
    );
}
