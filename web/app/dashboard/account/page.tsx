import { getProfile } from "@/lib/dal/profile";
import { PageHeader } from "@/components/dashboard/shell/PageHeader";
import { SectionShell } from "@/components/dashboard/shell/SectionShell";
import { ApiKeySection } from "@/components/dashboard/account/ApiKeySection";
import { Shield, Key, User } from "lucide-react";

export default async function AccountPage() {
    // 1. Fetch Data (Server-Side)
    const profile = await getProfile();

    return (
        <div className="p-4 md:p-8 max-w-[1600px] mx-auto min-h-screen flex flex-col gap-8">
            <PageHeader
                title="Account"
                description="Your profile and API settings."
                icon={User}
                iconColor="text-blue-400"
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <SectionShell
                    title="Profile Verification"
                    icon={Shield}
                >
                    <div className="space-y-4">
                        <div className="flex justify-between items-center py-2 border-b border-white/5">
                            <span className="text-xs text-zinc-500 uppercase tracking-tighter">Status</span>
                            <span className="text-xs bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20 font-bold uppercase tracking-widest">Active</span>
                        </div>
                        <div className="flex justify-between items-center py-2 border-b border-white/5">
                            <span className="text-xs text-zinc-500 uppercase tracking-tighter">Email</span>
                            <span className="text-xs text-white font-mono">{profile.email}</span>
                        </div>
                        <div className="flex justify-between items-center py-2 border-b border-white/5">
                            <span className="text-xs text-zinc-500 uppercase tracking-tighter">Plan</span>
                            <span className="text-xs text-white font-bold uppercase">{profile.tier}</span>
                        </div>
                    </div>
                </SectionShell>

                <ApiKeySection initialKey={profile.api_key} />
            </div>
        </div>
    );
}
