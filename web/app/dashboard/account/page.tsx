"use client";

import { Settings, Shield, Key, User } from "lucide-react";

export default function AccountPage() {
    return (
        <div className="p-4 md:p-8 max-w-[1600px] mx-auto min-h-screen flex flex-col gap-8">
            <div>
                <h1 className="text-3xl font-bold text-white tracking-tight mb-2 flex items-center gap-3">
                    <User className="w-8 h-8 text-blue-400" />
                    Account Control
                </h1>
                <p className="text-zinc-500">
                    Manage your Sidelith identity and system access.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-[#0c0c0e] border border-white/10 rounded-xl p-6">
                    <h3 className="text-white font-medium mb-4 flex items-center gap-2">
                        <Shield className="w-4 h-4 text-zinc-400" /> Profile Verification
                    </h3>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center py-2 border-b border-white/5">
                            <span className="text-xs text-zinc-500 uppercase tracking-tighter">Status</span>
                            <span className="text-xs bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20 font-bold uppercase tracking-widest">Active</span>
                        </div>
                        <div className="flex justify-between items-center py-2 border-b border-white/5">
                            <span className="text-xs text-zinc-500 uppercase tracking-tighter">Identity</span>
                            <span className="text-xs text-white font-mono">Judicial Egress Confirmed</span>
                        </div>
                    </div>
                </div>

                <div className="bg-[#0c0c0e] border border-white/10 rounded-xl p-6">
                    <h3 className="text-white font-medium mb-4 flex items-center gap-2">
                        <Key className="w-4 h-4 text-zinc-400" /> Security Keys
                    </h3>
                    <p className="text-xs text-zinc-500 mb-6">
                        Personal access tokens are currently managed via the main Registry dashboard.
                    </p>
                    <button className="w-full py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg border border-white/10 text-xs font-bold uppercase tracking-widest transition-colors">
                        Rotate All Secrets
                    </button>
                </div>
            </div>
        </div>
    );
}
