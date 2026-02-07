"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, Zap, Brain, Cpu, ShieldAlert, CheckCircle2 } from "lucide-react";

interface SPCData {
    spc_score: number;
    vectors: {
        silicon_velocity: number;
        temporal_synapse: number;
        cognitive_flow: number;
    };
    telemetry: {
        source: string;
        global_heat: number;
        local_heat: number;
        alerts?: { id: string, reason: string, file: string }[];
    };
    status: string;
    timestamp: string;
}

export default function HUDPage() {
    const [data, setData] = useState<SPCData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchSPC() {
            try {
                const res = await fetch("/api/spc");
                if (res.ok) {
                    const json = await res.json();
                    setData(json);
                }
            } catch (err) {
                console.error("Failed to fetch SPC:", err);
            } finally {
                setLoading(false);
            }
        }

        fetchSPC();
        const interval = setInterval(fetchSPC, 2000); // Pulse every 2s
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <motion.div
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="text-zinc-600 font-mono text-xs uppercase tracking-[0.5em]"
                >
                    Initalizing Perception HUD...
                </motion.div>
            </div>
        );
    }

    const spc = data?.spc_score || 0;
    const isFriction = data?.status === "FRICTION_SPIKE";
    const statusColor = isFriction ? "text-red-500" : spc < 0.6 ? "text-amber-500" : "text-[var(--color-neon-trace)]";

    return (
        <div className="min-h-screen bg-[#050505] text-white p-6 md:p-12 overflow-hidden flex flex-col font-sans relative">
            {/* Background Grid */}
            <div className="absolute inset-0 bg-grid-pattern opacity-20 pointer-events-none" />

            {/* Header */}
            <div className="flex justify-between items-start z-10">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <motion.div
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ duration: 2, repeat: Infinity }}
                            className={`w-2 h-2 rounded-full ${isFriction ? 'bg-red-500' : 'bg-[var(--color-neon-trace)]'}`}
                        />
                        <span className="text-[10px] uppercase tracking-[0.4em] text-zinc-500 font-black">System Hyper-Perception</span>
                    </div>
                    <h1 className="text-4xl font-black tracking-tighter italic glow-text">SYSTEM <span className="text-zinc-600">HUD</span></h1>
                </div>
                <div className="text-right">
                    <p className="text-[10px] font-mono text-zinc-600 uppercase tracking-widest">{new Date().toLocaleTimeString()}</p>
                    <p className="text-[10px] font-mono text-zinc-600 uppercase tracking-widest leading-none">ALPHA v1.0.8</p>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-8 mt-12 z-10">

                {/* Visualizer (Center) */}
                <div className="lg:col-span-2 flex flex-col items-center justify-center relative min-h-[400px]">
                    <motion.div
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        className="relative w-80 h-80 flex items-center justify-center"
                    >
                        {/* Outer Ring */}
                        <svg className="absolute inset-0 w-full h-full -rotate-90">
                            <circle
                                cx="160" cy="160" r="140"
                                fill="none"
                                stroke="rgba(255,255,255,0.05)"
                                strokeWidth="8"
                            />
                            <motion.circle
                                cx="160" cy="160" r="140"
                                fill="none"
                                stroke={isFriction ? "#ef4444" : "#10b981"}
                                strokeWidth="8"
                                strokeDasharray="880"
                                animate={{ strokeDashoffset: 880 - (880 * spc) }}
                                transition={{ type: "spring", damping: 20 }}
                                strokeLinecap="round"
                            />
                        </svg>

                        {/* Central Score */}
                        <div className="flex flex-col items-center">
                            <motion.span
                                key={spc}
                                initial={{ y: 20, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                className="text-8xl font-black tracking-tighter glow-text"
                            >
                                {spc.toFixed(2)}
                            </motion.span>
                            <span className={`text-xs font-black uppercase tracking-[0.3em] ${statusColor}`}>
                                {data?.status}
                            </span>
                        </div>

                        {/* Scan Lines or Pulses */}
                        <AnimatePresence>
                            <motion.div
                                animate={{ scale: [1, 1.4], opacity: [0.5, 0] }}
                                transition={{ duration: 2, repeat: Infinity }}
                                className={`absolute w-full h-full rounded-full border-2 ${isFriction ? 'border-red-500/20' : 'border-[var(--color-neon-trace)]/20'}`}
                            />
                        </AnimatePresence>
                    </motion.div>

                    {/* Vector Pulse Grid Below central score */}
                    <div className="mt-16 grid grid-cols-3 gap-12 w-full max-w-xl">
                        <VectorScore
                            label="Silicon"
                            value={data?.vectors.silicon_velocity || 0}
                            icon={<Cpu className="w-4 h-4" />}
                            color="text-cyan-400"
                        />
                        <VectorScore
                            label="Temporal"
                            value={data?.vectors.temporal_synapse || 0}
                            icon={<Zap className="w-4 h-4" />}
                            color="text-emerald-400"
                        />
                        <VectorScore
                            label="Cognitive"
                            value={data?.vectors.cognitive_flow || 0}
                            icon={<Brain className="w-4 h-4" />}
                            color="text-purple-400"
                        />
                    </div>
                </div>

                {/* Sidebar Metrics */}
                <div className="space-y-6">
                    <div className="glass-panel rounded-xl p-6 relative overflow-hidden group">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-xs uppercase tracking-widest text-zinc-500 flex items-center gap-2">
                                <Activity className="w-3 h-3" /> System Heartbeat
                            </h3>
                            {spc > 0.7 ? <CheckCircle2 className="w-4 h-4 text-emerald-500" /> : <ShieldAlert className="w-4 h-4 text-amber-500" />}
                        </div>
                        <div className="space-y-4 font-mono text-[10px] uppercase tracking-wider text-zinc-400">
                            <div className="flex justify-between border-b border-white/5 pb-2">
                                <span>Perception Index</span>
                                <span className="text-white">{(spc * 100).toFixed(1)}%</span>
                            </div>
                            <div className="flex justify-between border-b border-white/5 pb-2">
                                <span>Causal Confidence</span>
                                <span className="text-white">88%</span>
                            </div>
                            <div className="flex justify-between border-b border-white/5 pb-2">
                                <span>Friction Source</span>
                                <span className={data?.telemetry.source === 'EXTERNAL' ? 'text-amber-500' : 'text-white'}>
                                    {data?.telemetry.source || "OPTIMAL"}
                                </span>
                            </div>
                            <div className="flex justify-between border-b border-white/5 pb-2">
                                <span>Global Heat</span>
                                <span className="text-white">{((data?.telemetry.global_heat || 0) * 100).toFixed(0)}%</span>
                            </div>
                            <div className="flex justify-between border-b border-white/5 pb-2">
                                <span>Sidelith Load</span>
                                <span className="text-white">{((data?.telemetry.local_heat || 0) * 100).toFixed(0)}%</span>
                            </div>
                            <div className="flex justify-between border-b border-white/5 pb-2">
                                <span>Intent Latency</span>
                                <span className="text-white">28ms</span>
                            </div>
                            <div className="flex justify-between">
                                <span>System Guard</span>
                                <span className="text-emerald-500">ACTIVE</span>
                            </div>
                        </div>
                    </div>

                    <div className="glass-panel rounded-xl p-6">
                        <h3 className="text-xs uppercase tracking-widest text-zinc-500 mb-6 flex items-center gap-2">
                            <Cpu className="w-3 h-3" /> Machine State
                        </h3>
                        <div className="space-y-6">
                            <MachineMetric label="Perception Depth" value={74} />
                            <MachineMetric label="Memory Stability" value={92} />
                            <MachineMetric label="Strategic Alignment" value={85} />
                        </div>
                    </div>

                    <div className="glass-panel rounded-xl p-6">
                        <h3 className="text-xs uppercase tracking-widest text-zinc-500 mb-4 flex items-center gap-2">
                            <ShieldAlert className="w-3 h-3" /> Strategic Alerts
                        </h3>
                        <div className="space-y-3">
                            {data?.telemetry.alerts?.length === 0 ? (
                                <p className="text-[10px] text-zinc-600 italic">No violations detected.</p>
                            ) : (
                                data?.telemetry.alerts?.map((alert) => (
                                    <div key={alert.id} className="p-3 bg-red-500/5 border border-red-500/10 rounded-lg">
                                        <p className="text-[10px] font-black text-red-500 uppercase mb-1">{alert.file.split('/').pop()}</p>
                                        <p className="text-[10px] leading-relaxed text-zinc-400">{alert.reason}</p>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                    <div className="p-6">
                        <p className="text-[10px] text-zinc-600 italic leading-relaxed">
                            "The true measure of intelligence is not the speed of processing, but the fidelity of perception."
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

function VectorScore({ label, value, icon, color }: { label: string, value: number, icon: React.ReactNode, color: string }) {
    return (
        <div className="flex flex-col items-center gap-3">
            <div className={`p-3 rounded-full bg-white/[0.03] border border-white/5 ${color}`}>
                {icon}
            </div>
            <div className="text-center">
                <p className="text-[10px] uppercase tracking-widest text-zinc-500 mb-1 font-bold">{label}</p>
                <p className="text-2xl font-black tracking-tighter">{(value * 100).toFixed(0)}%</p>
            </div>
            <div className="w-12 h-1 bg-white/5 rounded-full overflow-hidden">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${value * 100}%` }}
                    className={`h-full ${color.replace('text-', 'bg-')}`}
                />
            </div>
        </div>
    );
}

function MachineMetric({ label, value }: { label: string, value: number }) {
    return (
        <div className="space-y-2">
            <div className="flex justify-between items-center text-[10px] uppercase tracking-widest font-bold">
                <span className="text-zinc-500">{label}</span>
                <span className="text-zinc-300">{value}%</span>
            </div>
            <div className="h-1 bg-white/[0.03] rounded-full overflow-hidden">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${value}%` }}
                    className="h-full bg-zinc-700"
                />
            </div>
        </div>
    );
}
