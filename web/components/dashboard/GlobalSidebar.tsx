"use client";

import { cn } from "@/lib/utils";
import { RotatingRole } from "@/components/ui/RotatingRole";
import { usePathname } from "next/navigation";
import Link from "next/link";
import {
    BarChart3,
    Brain,
    CreditCard,
    FileText,
    Home,
    Settings,
    Shield,
    Zap,
    LogOut,
    ChevronRight,
    Menu,
    X
} from "lucide-react";
import { useState, useEffect } from "react";

const SIDEBAR_ITEMS = [
    {
        category: "Context Engine",
        items: [
            { label: "The Vault", href: "/dashboard", icon: Home },
            { label: "Trajectory Variance", href: "/dashboard/impact", icon: BarChart3 },
            { label: "The Event Clock", href: "/dashboard/ledger", icon: FileText },
        ]
    },
    {
        category: "Infrastructure",
        items: [
            { label: "Sovereign Capacity", href: "/dashboard/billing", icon: CreditCard },
            { label: "Neural Extensions", href: "/dashboard/addons", icon: Zap },
        ]
    },
    {
        category: "Registry Settings",
        items: [
            { label: "Privacy & Data", href: "/dashboard/settings", icon: Shield },
            { label: "Account Control", href: "/dashboard/account", icon: Settings },
        ]
    }
];

export function GlobalSidebar() {
    const pathname = usePathname();
    const [isOpen, setIsOpen] = useState(false);

    // Close sidebar on route change
    useEffect(() => {
        setIsOpen(false);
    }, [pathname]);

    return (
        <>
            {/* Mobile Header Trigger */}
            <div className="md:hidden fixed top-0 left-0 right-0 h-16 border-b border-white/10 bg-[#0c0c0e]/95 backdrop-blur-md z-50 flex items-center justify-between px-4">
                <Link href="/" className="flex items-center gap-2.5">
                    <div className="w-5 h-5 bg-white rounded-sm" />
                    <span className="font-bold tracking-tight text-white uppercase italic">Side<span className="not-italic lowercase font-light text-zinc-500">lith</span></span>
                    <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded border border-emerald-500/20 ml-1 font-black uppercase">Sovereign</span>
                </Link>
                <button
                    onClick={() => setIsOpen(!isOpen)}
                    className="p-2 text-zinc-400 hover:text-white"
                >
                    {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                </button>
            </div>

            {/* Overlay for mobile */}
            {isOpen && (
                <div
                    className="md:hidden fixed inset-0 bg-black/80 z-40 backdrop-blur-sm"
                    onClick={() => setIsOpen(false)}
                />
            )}

            {/* Sidebar Container */}
            <aside className={cn(
                "fixed md:sticky top-0 left-0 z-50 h-screen w-64 bg-[#0c0c0e] border-r border-white/10 flex flex-col transition-transform duration-300 ease-in-out md:translate-x-0",
                isOpen ? "translate-x-0" : "-translate-x-full"
            )}>
                <Link href="/" className="hidden md:flex h-16 items-center px-6 border-b border-white/5 gap-2.5 group">
                    <div className="w-5 h-5 bg-white rounded-sm group-hover:rotate-90 transition-transform duration-500" />
                    <span className="font-bold tracking-tight text-white uppercase italic">Side<span className="not-italic lowercase font-light text-zinc-500">lith</span></span>
                    <span className="text-[10px] bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded border border-emerald-500/20 ml-1 font-black uppercase">Sovereign</span>
                </Link>

                {/* Navigation */}
                <div className="flex-1 overflow-y-auto py-6 px-3 space-y-8 mt-16 md:mt-0">
                    {SIDEBAR_ITEMS.map((section, i) => (
                        <div key={i}>
                            <h4 className="px-3 text-xs font-mono text-zinc-500 uppercase tracking-widest mb-2 select-none">
                                {section.category}
                            </h4>
                            <div className="space-y-0.5">
                                {section.items.map((item) => {
                                    const isActive = pathname === item.href;
                                    const Icon = item.icon;

                                    return (
                                        <Link
                                            key={item.href}
                                            href={item.href}
                                            className={cn(
                                                "group flex items-center justify-between px-3 py-2 rounded-md transition-all duration-200 text-sm font-medium",
                                                isActive
                                                    ? "bg-white/10 text-white shadow-sm ring-1 ring-white/5"
                                                    : "text-zinc-400 hover:text-white hover:bg-white/5"
                                            )}
                                        >
                                            <div className="flex items-center gap-3">
                                                <Icon className={cn(
                                                    "w-4 h-4 transition-colors",
                                                    isActive ? "text-emerald-400" : "text-zinc-500 group-hover:text-zinc-300"
                                                )} />
                                                <span>{item.label}</span>
                                            </div>
                                            {isActive && (
                                                <ChevronRight className="w-3 h-3 text-white/50 animate-in fade-in slide-in-from-left-1" />
                                            )}
                                        </Link>
                                    );
                                })}
                            </div>
                        </div>
                    ))}
                </div>

                {/* User Footer */}
                <div className="p-4 border-t border-white/5">
                    <div className="px-2 pb-3">
                        <div className="text-[10px] font-medium text-zinc-600 uppercase tracking-wider leading-relaxed">
                            <RotatingRole prefix="Sidelith: The " suffix=" on your side." />
                        </div>
                    </div>
                    <button className="flex items-center gap-3 w-full p-2 rounded-md hover:bg-white/5 transition-colors group">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 border border-white/10" />
                        <div className="text-left flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate group-hover:text-cyan-200">Erhan Erdogan</p>
                            <p className="text-xs text-zinc-500 truncate">erhan@sidelith.com</p>
                        </div>
                        <LogOut className="w-4 h-4 text-zinc-600 group-hover:text-red-400 transition-colors" />
                    </button>
                </div>
            </aside>
        </>
    );
}
