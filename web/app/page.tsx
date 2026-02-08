"use client";

import { Header } from "@/components/Header";
import { Hero } from "@/components/landing/Hero";
import { ProblemSection } from "@/components/landing/ProblemSection";
import { MiddlewareFlow } from "@/components/landing/MiddlewareFlow";
import { StruggleBento } from "@/components/landing/StruggleBento";
import { SolutionSolarSystem } from "@/components/landing/SolutionSolarSystem";
import { DefensiveMoats } from "@/components/landing/DefensiveMoats";
import { CollectiveIntelligence } from "@/components/landing/CollectiveIntelligence";
import { PricingSection } from "@/components/landing/PricingSection";
import { InstallSection } from "@/components/landing/InstallSection";
import { LandingFooter } from "@/components/landing/LandingFooter";

export default function LandingPage() {
    return (
        <main className="min-h-screen bg-[#050505] text-white flex flex-col items-center selection:bg-neon selection:text-black">
            <Header />

            <Hero />

            <div className="w-full flex flex-col items-center">
                <ProblemSection />
                <MiddlewareFlow />
                <StruggleBento />
                <SolutionSolarSystem />
                <DefensiveMoats />
                <CollectiveIntelligence />
                <PricingSection />
                <InstallSection />
            </div>

            <LandingFooter />

            {/* Background Grid */}
            <div className="fixed inset-0 z-0 pointer-events-none bg-grid-pattern opacity-20" />
        </main>
    );
}
