import { getSettings } from "@/lib/dal/settings";
import { PageHeader } from "@/components/dashboard/shell/PageHeader";
import { Shield } from "lucide-react";
import { GhostModeSection } from "@/components/dashboard/settings/GhostModeSection";
import { DataPrivacy } from "@/components/dashboard/settings/DataPrivacy";
import { DangerZone } from "@/components/dashboard/settings/DangerZone";

export default async function SettingsPage() {
    // 1. Fetch Data (Server-Side)
    const settings = await getSettings();

    return (
        <div className="p-4 md:p-8 max-w-[1200px] mx-auto min-h-screen flex flex-col gap-8 mt-16 md:mt-0">
            <PageHeader
                title="Privacy & Data"
                description='System control over your context. Sidelith is designed to be "Local First", giving you absolute authority over data egress.'
                icon={Shield}
                iconColor="text-emerald-500"
            />

            {/* Ghost Mode Toggle (Hero Feature) */}
            <GhostModeSection initialEnabled={settings.ghost_mode} />

            {/* Data Privacy Grid */}
            <DataPrivacy />

            {/* Danger Zone */}
            <DangerZone />
        </div>
    );
}
