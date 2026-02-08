"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";

const sections = [
    { id: "quickstart", name: "Quickstart" },
    { id: "how-it-works", name: "How It Works" },
    { id: "cli-reference", name: "CLI Reference" },
    { id: "troubleshooting", name: "Troubleshooting" },
];

export function Sidebar() {
    const [activeSection, setActiveSection] = useState("");

    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        setActiveSection(entry.target.id);
                    }
                });
            },
            { rootMargin: "-20% 0% -35% 0%" }
        );

        sections.forEach((section) => {
            const element = document.getElementById(section.id);
            if (element) observer.observe(element);
        });

        return () => observer.disconnect();
    }, []);

    return (
        <aside className="w-64 hidden lg:block shrink-0 sticky top-24 self-start h-[calc(100vh-6rem)] overflow-y-auto pr-8">
            <nav className="space-y-1">
                {sections.map((section) => (
                    <Link
                        key={section.id}
                        href={`#${section.id}`}
                        className={cn(
                            "block px-4 py-2 text-sm font-medium rounded-lg transition-all",
                            activeSection === section.id
                                ? "bg-white/5 text-white"
                                : "text-white/60 hover:text-white hover:bg-white/5"
                        )}
                    >
                        {section.name}
                    </Link>
                ))}
            </nav>
        </aside>
    );
}
