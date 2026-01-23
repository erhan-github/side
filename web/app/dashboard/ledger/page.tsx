import { getLedger } from "@/lib/dal/ledger";
import { PageHeader } from "@/components/dashboard/shell/PageHeader";
import { FileText, Filter, Download, Search, CheckCircle, Clock, AlertCircle } from "lucide-react";

export default async function LedgerPage() {
    const ledger = await getLedger();

    return (
        <div className="p-4 md:p-8 max-w-[1600px] mx-auto min-h-screen flex flex-col gap-6 mt-16 md:mt-0">
            <PageHeader
                title="Forensic Ledger"
                description="Immutable record of all strategic operations. Every token consumption is tracked."
                icon={FileText}
                iconColor="text-purple-400"
                action={
                    <div className="flex items-center gap-2 w-full md:w-auto">
                        <div className="relative flex-1 md:flex-none">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-zinc-500" />
                            <input
                                type="text"
                                placeholder="Search hash or operation..."
                                className="w-full md:w-64 bg-[#0c0c0e] border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-purple-500/50 transition-colors"
                            />
                        </div>
                        <button className="bg-white/5 hover:bg-white/10 text-white p-2 rounded-lg border border-white/10 transition-colors">
                            <Filter className="w-4 h-4" />
                        </button>
                        <button className="bg-white/5 hover:bg-white/10 text-white p-2 rounded-lg border border-white/10 transition-colors">
                            <Download className="w-4 h-4" />
                        </button>
                    </div>
                }
            />

            {/* Table Container */}
            <div className="bg-[#0c0c0e] border border-white/10 rounded-xl overflow-hidden flex-1 flex flex-col">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm whitespace-nowrap">
                        <thead className="bg-zinc-900/50 text-zinc-500 font-mono uppercase text-xs border-b border-white/5">
                            <tr>
                                <th className="px-6 py-4 font-normal">Timestamp</th>
                                <th className="px-6 py-4 font-normal">Operation</th>
                                <th className="px-6 py-4 font-normal">Subject</th>
                                <th className="px-6 py-4 font-normal text-right">Tokens</th>
                                <th className="px-6 py-4 font-normal text-right">Cost</th>
                                <th className="px-6 py-4 font-normal text-center">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {ledger.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-8 text-center text-zinc-500">
                                        No entries found in ledger.
                                    </td>
                                </tr>
                            ) : (
                                ledger.map((log, i) => (
                                    <tr key={log.id || i} className="group hover:bg-white/[0.02] transition-colors cursor-pointer">
                                        <td className="px-6 py-4 font-mono text-zinc-400 text-xs">
                                            {new Date(log.created_at).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2 py-1 rounded text-[10px] font-bold border 
                                                ${log.operation === "AUDIT" ? "bg-red-500/10 text-red-400 border-red-500/20" :
                                                    log.operation === "PLAN" ? "bg-blue-500/10 text-blue-400 border-blue-500/20" :
                                                        "bg-zinc-500/10 text-zinc-400 border-zinc-500/20"
                                                }`}>
                                                {log.operation.toUpperCase()}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-white font-medium">
                                            -
                                        </td>
                                        <td className="px-6 py-4 text-right text-zinc-400 font-mono text-xs">
                                            {log.tokens.toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 text-right text-white font-mono text-xs">
                                            ${log.cost.toFixed(4)}
                                        </td>
                                        <td className="px-6 py-4 text-center flex justify-center">
                                            {log.status === "success" ? (
                                                <CheckCircle className="w-4 h-4 text-emerald-500/50" />
                                            ) : (
                                                <AlertCircle className="w-4 h-4 text-yellow-500/50" />
                                            )}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
