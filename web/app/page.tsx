"use client";

import { Header } from "@/components/Header";
import { Hero } from "@/components/landing/Hero";
import { ProblemSection } from "@/components/landing/ProblemSection";
import { MiddlewareFlow } from "@/components/landing/MiddlewareFlow";
import { StruggleBento } from "@/components/landing/StruggleBento";
import { ComparisonGallery } from "@/components/landing/ComparisonGallery";
import { IntelligenceLoop } from "@/components/landing/IntelligenceLoop";
import { DefensiveMoats } from "@/components/landing/DefensiveMoats";
import { PricingSection } from "@/components/landing/PricingSection";
import { InstallSection } from "@/components/landing/InstallSection";
import { LandingFooter } from "@/components/landing/LandingFooter";

export default function LandingPage() {
    return (
        <main className="min-h-screen bg-[#050505] text-white flex flex-col items-start selection:bg-neon selection:text-black">
            <Hero />

            <div className="w-full flex flex-col items-center">
                <ProblemSection />
                <MiddlewareFlow />
                <StruggleBento />
                <ComparisonGallery />
                <IntelligenceLoop />
                <DefensiveMoats />
                <PricingSection />
                <InstallSection />
            </div>

            {/* Background Grid */}
            <div className="fixed inset-0 z-0 pointer-events-none bg-grid-pattern opacity-20" />
        </main>
    );
}
