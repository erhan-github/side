import { NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import path from 'path';

export async function GET() {
    try {
        // [PALANTIR EFFICIENCY]: No more spawning Python!
        // We read the pre-calculated metrics from the JSON bridge.
        const rootDir = process.env.ROOT_DIR || path.resolve(process.cwd(), '..');
        const pulsePath = path.join(rootDir, '.side', 'pulse.json');

        const data = await readFile(pulsePath, 'utf-8');
        return NextResponse.json(JSON.parse(data));

    } catch (error: any) {
        // If file doesn't exist yet, return a graceful "Optimizing..." state
        if (error.code === 'ENOENT') {
            return NextResponse.json({
                status: "OPTIMIZING",
                spc_score: 1.0,
                vectors: { silicon_velocity: 1.0, temporal_synapse: 1.0, cognitive_flow: 1.0 }
            });
        }

        console.error('API Route Error:', error);
        return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
    }
}
