#!/usr/bin/env node
/**
 * Side MCP - The Strategic Partner that thinks for you.
 * 
 * This is the entry point for `npx @side-ai/mcp`.
 * It spawns the Python MCP server with proper configuration.
 */

const { spawn } = require('child_process');
const path = require('path');

// Check for SIDE_API_KEY
const apiKey = process.env.SIDE_API_KEY;
if (!apiKey) {
    console.error(`
╔════════════════════════════════════════════════════════════╗
║                        Side MCP                           ║
╠════════════════════════════════════════════════════════════╣
║  ⚠️  SIDE_API_KEY not found                                ║
║                                                            ║
║  Get your free API key at:                                 ║
║  https://sidelith.com/dashboard                                 ║
║                                                            ║
║  Then add to your MCP config:                              ║
║  "env": { "SIDE_API_KEY": "sk_xxx" }                       ║
╚════════════════════════════════════════════════════════════╝
`);
    process.exit(1);
}

console.log(`
╔════════════════════════════════════════════════════════════╗
║                     Side MCP v1.0.0                        ║
║        The Strategic Partner that thinks for you           ║
╚════════════════════════════════════════════════════════════╝

✅ API Key found: ${apiKey.slice(0, 10)}...
🚀 Starting Side MCP server...
`);

// Spawn Python MCP server
const pythonPath = process.env.SIDE_PYTHON || 'python3';
const serverModule = 'side.server';

const child = spawn(pythonPath, ['-m', serverModule], {
    stdio: 'inherit',
    env: {
        ...process.env,
        SIDE_API_KEY: apiKey,
        SIDE_CLOUD_MODE: 'true',
    },
});

child.on('error', (err) => {
    console.error(`Failed to start Side MCP: ${err.message}`);
    console.error(`
Troubleshooting:
1. Ensure Python 3.11+ is installed
2. Install Side: pip install side-ai
3. Or use: python -m side.server
`);
    process.exit(1);
});

child.on('close', (code) => {
    process.exit(code);
});
