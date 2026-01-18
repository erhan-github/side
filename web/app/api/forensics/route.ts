import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function GET(request: Request) {
    try {
        const { searchParams } = new URL(request.url);
        const action = searchParams.get('action') || 'alerts';

        // Path to the Python MCP server
        const projectRoot = process.cwd();
        const pythonPath = `${projectRoot}/../cso-ai/.venv/bin/python`;

        let result;

        switch (action) {
            case 'alerts':
                // Get strategic alerts
                result = await execAsync(
                    `${pythonPath} -c "from cso_ai.intel.forensic_engine import ForensicEngine; from cso_ai.intel.intelligence_store import IntelligenceStore; from cso_ai.storage.simple_db import SimplifiedDatabase; from pathlib import Path; import json; root = Path('${projectRoot}/../cso-ai'); engine = ForensicEngine(str(root)); db = SimplifiedDatabase(str(root / '.cso' / 'local.db')); store = IntelligenceStore(db); project_id = SimplifiedDatabase.get_project_id(root); findings = engine.scan(); store.store_findings(project_id, findings); alerts = store.get_active_findings(project_id); print(json.dumps(alerts))"`
                );
                return NextResponse.json(JSON.parse(result.stdout));

            case 'iq':
                // Get Strategic IQ
                result = await execAsync(
                    `${pythonPath} -c "from cso_ai.intel.intelligence_store import IntelligenceStore; from cso_ai.storage.simple_db import SimplifiedDatabase; from pathlib import Path; import json; root = Path('${projectRoot}/../cso-ai'); db = SimplifiedDatabase(str(root / '.cso' / 'local.db')); store = IntelligenceStore(db); project_id = SimplifiedDatabase.get_project_id(root); score = store.get_strategic_iq(project_id); stats = store.get_finding_stats(project_id); print(json.dumps({'score': score, 'stats': stats}))"`
                );
                return NextResponse.json(JSON.parse(result.stdout));

            default:
                return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
        }
    } catch (error: any) {
        console.error('API Error:', error);
        return NextResponse.json(
            { error: error.message || 'Internal server error' },
            { status: 500 }
        );
    }
}

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { action, finding_id } = body;

        if (action === 'resolve' && finding_id) {
            const projectRoot = process.cwd();
            const pythonPath = `${projectRoot}/../cso-ai/.venv/bin/python`;

            await execAsync(
                `${pythonPath} -c "from cso_ai.intel.intelligence_store import IntelligenceStore; from cso_ai.storage.simple_db import SimplifiedDatabase; from pathlib import Path; root = Path('${projectRoot}/../cso-ai'); db = SimplifiedDatabase(str(root / '.cso' / 'local.db')); store = IntelligenceStore(db); store.resolve_finding('${finding_id}')"`
            );

            return NextResponse.json({ success: true });
        }

        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    } catch (error: any) {
        console.error('API Error:', error);
        return NextResponse.json(
            { error: error.message || 'Internal server error' },
            { status: 500 }
        );
    }
}
