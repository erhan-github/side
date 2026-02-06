"use client";

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { FixedSizeList as List } from 'react-window';
import { Shield, AlertCircle, Clock, Search, Filter } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Finding {
    id: string;
    project_id: string;
    type: string;
    severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    message: string;
    file_path?: string;
    line_number?: number;
    created_at: string;
    metadata?: any;
    is_resolved: boolean;
}

const SEVERITY_COLORS = {
    LOW: "text-blue-400 border-blue-500/20 bg-blue-500/5",
    MEDIUM: "text-yellow-400 border-yellow-500/20 bg-yellow-500/5",
    HIGH: "text-orange-400 border-orange-500/20 bg-orange-500/5",
    CRITICAL: "text-red-400 border-red-500/20 bg-red-500/5",
};

const PAGE_SIZE = 50;

export function ArtifactGallery() {
    const [findings, setFindings] = useState<Finding[]>([]);
    const [totalCount, setTotalCount] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const listRef = useRef<List>(null);

    const fetchFindings = useCallback(async (offset: number) => {
        try {
            const response = await fetch(`/api/forensics?action=alerts&limit=${PAGE_SIZE}&offset=${offset}`);
            if (!response.ok) throw new Error("Failed to fetch findings");
            const { data, count } = await response.json();

            setFindings(prev => {
                const updated = [...prev];
                data.forEach((item: Finding, index: number) => {
                    updated[offset + index] = item;
                });
                return updated;
            });
            setTotalCount(count);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchFindings(0);
    }, [fetchFindings]);

    const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
        const finding = findings[index];

        if (!finding) {
            // Load more if we hit a gap
            if (!isLoading) {
                fetchFindings(Math.floor(index / PAGE_SIZE) * PAGE_SIZE);
            }
            return <div style={style} className="p-4 border-b border-white/5 animate-pulse bg-white/5" />;
        }

        return (
            <div style={style} className="p-4 flex flex-col gap-2 border-b border-white/5 hover:bg-white/[0.02] transition-colors group">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <span className={cn(
                            "px-1.5 py-0.5 rounded text-[10px] font-bold uppercase border tracking-widest",
                            SEVERITY_COLORS[finding.severity]
                        )}>
                            {finding.severity}
                        </span>
                        <span className="text-sm font-medium text-white/90 truncate max-w-[400px]">
                            {finding.message}
                        </span>
                    </div>
                    <div className="flex items-center gap-3 text-[10px] text-zinc-500 font-mono">
                        <Clock className="w-3 h-3" />
                        <span>{new Date(finding.created_at).toLocaleString()}</span>
                    </div>
                </div>

                <div className="flex items-center gap-4 text-xs text-zinc-500">
                    <div className="flex items-center gap-1">
                        <Search className="w-3 h-3" />
                        <span>{finding.type}</span>
                    </div>
                    {finding.file_path && (
                        <div className="flex items-center gap-1 font-mono text-[10px] text-zinc-400">
                            <span>{finding.file_path}</span>
                            {finding.line_number && <span>:{finding.line_number}</span>}
                        </div>
                    )}
                </div>

                {/* Simulated High-Res Artifact Image (Lazy Loaded via decoding="async") */}
                {finding.metadata?.image && (
                    <div className="mt-2 relative rounded overflow-hidden border border-white/5 bg-black/20 w-full h-[120px]">
                        <img
                            src={finding.metadata.image}
                            alt="Artifact Preview"
                            loading="lazy"
                            decoding="async"
                            className="w-full h-full object-cover opacity-60 group-hover:opacity-100 transition-opacity"
                        />
                    </div>
                )}
            </div>
        );
    };

    if (error) {
        return (
            <div className="p-8 text-center text-red-400 flex flex-col items-center gap-3">
                <AlertCircle className="w-8 h-8" />
                <p>Error loading artifacts: {error}</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-[#0c0c0e] border border-white/10 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-white/10 flex items-center justify-between bg-zinc-900/50">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded bg-purple-500/10 text-purple-400">
                        <Shield className="w-5 h-5" />
                    </div>
                    <div>
                        <h2 className="text-lg font-bold text-white">Forensic Findings</h2>
                        <p className="text-xs text-zinc-500">Virtual Neural Surface • {totalCount.toLocaleString()} Entries</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button className="p-2 rounded hover:bg-white/5 text-zinc-400 transition-colors">
                        <Filter className="w-4 h-4" />
                    </button>
                </div>
            </div>

            <div className="flex-1 min-h-[500px]">
                {totalCount > 0 ? (
                    <List
                        ref={listRef}
                        height={600}
                        itemCount={totalCount}
                        itemSize={140}
                        width="100%"
                        className="custom-scrollbar"
                    >
                        {Row}
                    </List>
                ) : (
                    !isLoading && (
                        <div className="h-full flex flex-col items-center justify-center text-zinc-600 italic gap-4">
                            <Shield className="w-12 h-12 opacity-20" />
                            <p>No findings detected in the current audit window.</p>
                        </div>
                    )
                )}
                {isLoading && findings.length === 0 && (
                    <div className="h-full flex items-center justify-center">
                        <div className="w-8 h-8 border-2 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
                    </div>
                )}
            </div>
        </div>
    );
}
