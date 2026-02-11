import { getBillingStatus } from "@/lib/dal/billing";
import { PageHeader } from "@/components/dashboard/shell/PageHeader";
import { CreditCard, ExternalLink, ShieldCheck } from "lucide-react";
import { RefuelAction } from "@/components/dashboard/billing/RefuelAction";
export default async function BillingPage() {
    const billing = await getBillingStatus();

    const percentage = Math.min(100, (billing.capacity.used / billing.capacity.limit) * 100);

    return (
        <div className="p-4 md:p-8 max-w-[1200px] mx-auto min-h-screen flex flex-col gap-8 mt-16 md:mt-0">
            <PageHeader
                title="Billing"
                description="Manage your Side Units and subscription."
                icon={CreditCard}
                iconColor="text-blue-500"
                action={
                    <div className="flex items-center gap-3 bg-blue-500/10 border border-blue-500/20 px-4 py-2 rounded-lg">
                        <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                        <span className="text-blue-400 font-medium text-sm border-r border-blue-500/20 pr-3 mr-1 uppercase">Plan</span>
                        <span className="text-white font-bold uppercase">{billing.plan}</span>
                    </div>
                }
            />

            {/* Main Capacity Card */}
            <div className="bg-[#0c0c0e] border border-white/10 rounded-2xl p-6 md:p-8 relative overflow-hidden">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                    {/* Left: Usage Radial/Bar */}
                    <div className="md:col-span-2 flex flex-col justify-between gap-8">
                        <div>
                            <h3 className="text-lg font-medium text-white mb-1">Side Units Balance</h3>
                            <p className="text-sm text-zinc-500 mb-6">Resets on {new Date(billing.capacity.resetDate).toLocaleDateString()}</p>

                            {/* Big Progress Bar (Segmented Style) */}
                            <div className="flex bg-zinc-800/30 rounded-full h-4 overflow-hidden p-[2px] gap-[2px] mb-2">
                                {[...Array(40)].map((_, i) => {
                                    const blockValue = 100 / 40; // 2.5% per block
                                    const isFilled = percentage >= (i + 1) * blockValue;

                                    return (
                                        <div
                                            key={i}
                                            className={`flex-1 rounded-[1px] transition-all duration-300 ${isFilled ? "bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.6)]" : "bg-white/5"
                                                }`}
                                        />
                                    )
                                })}
                            </div>
                            <div className="flex justify-between text-xs font-mono text-zinc-500 uppercase tracking-widest">
                                <span>Used: {billing.capacity.used.toLocaleString()} SU</span>
                                <span>Limit: {billing.capacity.limit.toLocaleString()} SU</span>
                            </div>
                        </div>
                    </div>

                    {/* Right: Actions */}
                    <div className="border-l border-white/10 pl-0 md:pl-12 flex flex-col justify-between gap-8 h-full">
                        <div className="space-y-3 pt-4">
                            <RefuelAction />
                            <div className="text-center">
                                <span className="text-xs text-zinc-500">Unbilled: </span>
                                <span className="text-white font-mono text-sm">$0.00</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Invoices & Subscription Management (Portal) */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-[#0c0c0e] border border-white/10 rounded-xl p-6 flex flex-col justify-between">
                    <div>
                        <h3 className="text-white font-medium mb-2 flex items-center gap-2">
                            Need More Side Units?
                        </h3>
                        <p className="text-sm text-zinc-500">
                            Buy additional units without changing your plan. Perfect for high-intensity development bursts.
                        </p>
                    </div>
                </div>

                <div className="bg-[#0c0c0e] border border-white/10 rounded-xl p-6 flex flex-col justify-between items-start">
                    <div>
                        <h3 className="text-white font-medium mb-2">Subscription & Invoices</h3>
                        <p className="text-sm text-zinc-500 mb-4">
                            View your full billing history, download official PDF invoices, and manage your payment methods.
                        </p>
                    </div>

                    {billing.portalUrl ? (
                        <a
                            href={billing.portalUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-2 px-4 py-2 bg-white text-black text-sm font-medium rounded-lg hover:bg-zinc-200 transition-colors"
                        >
                            Open Billing Portal <ExternalLink className="w-4 h-4" />
                        </a>
                    ) : (
                        <div className="text-xs text-zinc-600 font-mono bg-zinc-900 px-3 py-2 rounded border border-zinc-800">
                            No active billing account linked yet.
                        </div>
                    )}
                </div>
            </div>
        </div >
    );
}
