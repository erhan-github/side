import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { Zap, Copy, Terminal, Key, Check } from "lucide-react";
import Link from "next/link";
import { CheckoutButton } from "@/components/dashboard/CheckoutButton";
import { AuthSync } from "@/components/auth/AuthSync";

export default async function DashboardPage() {
    const supabase = await createClient();

    const {
        data: { user },
        error
    } = await supabase.auth.getUser();

    // SOFT GATE: If no user on server, return a "skeleton" or loading state
    // The <AuthSync /> component in the root layout will force a refresh 
    // once the client-side cookie is detected.
    if (error || !user) {
        console.warn("[DASHBOARD] Server-side auth missing. Waiting for client hydration...");
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-8 h-8 border-t-2 border-cyan-500 rounded-full animate-spin"></div>
                    <p className="text-zinc-500 font-mono text-xs uppercase tracking-widest">Hydrating Secure Session...</p>
                </div>
            </div>
        );
    }

    console.log(`[DASHBOARD] Session Verified: User ID ${user.id}`);

    // Fetch Profile for API Key
    let { data: profile } = await supabase
        .from("profiles")
        .select("*")
        .eq("id", user.id)
        .single();

    // Auto-create profile if it doesn't exist (e.g., user signed up before trigger was live)
    if (!profile) {
        const { data: newProfile, error: createError } = await supabase
            .from("profiles")
            .insert({
                id: user.id,
                email: user.email,
                api_key: `sk_${Math.random().toString(36).substring(2, 15)}${Math.random().toString(36).substring(2, 15)}`
            })
            .select()
            .single();

        if (!createError) {
            profile = newProfile;
        }
    }

    const apiKey = profile?.api_key || "Generating...";
    const tier = profile?.tier || "free";
    const tokens = profile?.tokens_monthly || 10000;
    const tokensUsed = profile?.tokens_used || 0;

    return (
        <div className="min-h-screen bg-black text-white p-8">
            <div className="max-w-4xl mx-auto space-y-8">
                {/* Header */}
                <div className="flex justify-between items-end border-b border-white/10 pb-6">
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <div className="w-3 h-3 bg-cyan-500 rounded-sm animate-pulse" />
                            <span className="text-xs uppercase tracking-[0.3em] text-zinc-500 font-bold">System of Record</span>
                        </div>
                        <h1 className="text-4xl font-bold tracking-tighter">Sidelith <span className="text-zinc-500 font-light text-2xl ml-2">Registry</span></h1>
                        <p className="text-zinc-400 mt-2 italic">Welcome back, {user.user_metadata.full_name || user.email}</p>
                    </div>
                    <div className="text-right">
                        <span className="text-xs uppercase tracking-[0.2em] text-zinc-400 font-black">Infrastructure Tier</span>
                        <p className="font-black text-2xl uppercase tracking-tighter text-white">{tier}</p>
                    </div>
                </div>

                {/* API Key Section */}
                <div className="bg-zinc-900 border border-white/10 rounded-xl p-8 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                        <Key className="w-32 h-32" />
                    </div>
                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <Terminal className="w-5 h-5 text-cyan-400" />
                        Registry Credentials
                    </h2>
                    <div className="space-y-3 mb-8 text-sm text-zinc-300 font-medium">
                        <p className="flex items-center gap-2 text-white">
                            <Check className="w-4 h-4 text-green-400" /> 100% Judicial Sync (Sanitized)
                        </p>
                        <p className="flex items-center gap-2">
                            <Check className="w-4 h-4 text-green-400" /> Bidirectional Monolith Updates
                        </p>
                        <p className="flex items-center gap-2">
                            <Check className="w-4 h-4 text-green-400" /> Sovereign Egress (GDPR Compliant)
                        </p>
                    </div>

                    <div className="bg-black/50 border border-white/5 rounded-lg p-5 flex items-center justify-between font-mono text-sm group-hover:border-cyan-500/30 transition-colors">
                        <div className="flex flex-col">
                            <span className="text-xs text-zinc-600 mb-1 uppercase tracking-tighter">Secret ID</span>
                            <span className="text-green-400 truncate mr-4 text-base">{apiKey}</span>
                        </div>
                        <div className="text-[10px] text-zinc-700 uppercase tracking-widest font-bold border border-zinc-800 px-2 py-1 rounded">Read Only</div>
                    </div>
                </div>

                {/* Usage & Billing */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-zinc-900 border border-white/10 rounded-xl p-6">
                        <h3 className="text-lg font-semibold mb-2">Registry Capacity</h3>
                        <div className="mt-4">
                            <div className="flex justify-between text-sm mb-2 font-bold uppercase tracking-tighter">
                                <span className="text-zinc-400">Registry Throughput</span>
                                <span className="font-mono text-white">{tokens.toLocaleString()} SUs</span>
                            </div>
                            <div className="h-3 bg-white/5 rounded-full overflow-hidden border border-white/10">
                                <div
                                    className="h-full bg-cyan-500 transition-all duration-1000"
                                    style={{ width: `${Math.min(100, (tokensUsed / tokens) * 100)}%` }}
                                />
                            </div>
                            <p className="text-[10px] text-zinc-500 mt-2 uppercase tracking-widest font-black">Capacity Resets Feb 1st</p>
                        </div>
                    </div>

                    <div className="bg-zinc-900 border border-white/10 rounded-xl p-6 flex flex-col justify-center items-center text-center group">
                        <div className="w-12 h-12 bg-cyan-500/10 rounded-full flex items-center justify-center mb-4 group-hover:bg-cyan-500/20 transition-all">
                            <Zap className="w-6 h-6 text-cyan-500" />
                        </div>
                        <h3 className="font-bold text-lg mb-4 uppercase tracking-tighter italic">Evolve to Pro</h3>
                        <div className="space-y-2 mb-6 text-xs text-zinc-500">
                            <p>• 5,000 SUs Monthly</p>
                            <p>• Architectural Forensics</p>
                            <p>• Priority Infrastructure</p>
                        </div>

                        <CheckoutButton
                            variantId={process.env.LEMONSQUEEZY_VARIANT_ID_PRO!}
                            label="EVOLVE NOW ($20)"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
