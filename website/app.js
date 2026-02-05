const integrations = {
    claude: {
        title: "Claude Desktop Implementation",
        steps: [
            "1. Open <code>~/Library/Application Support/Claude/claude_desktop_config.json</code>",
            "2. Add the Sidelith MCP tool bridge definition.",
            "3. Run <code>side connect --mcp</code> in your terminal.",
            "4. Claude is now siloed behind the Sovereign Shield."
        ]
    },
    cursor: {
        title: "Cursor Editor Implementation",
        steps: [
            "1. Go to <b>Cursor Settings > Features > MCP</b>",
            "2. Add New MCP Server: <code>Sidelith</code>",
            "3. Use Command: <code>side connect cursor</code>",
            "4. Your reasoning is now anchored to the project's sovereign intent."
        ]
    },
    antigravity: {
        title: "Antigravity AI Implementation",
        steps: [
            "1. In your global command bar, type <code>/side connect</code>",
            "2. Antigravity will auto-detect the local <code>.side-id</code>",
            "3. Context is piped via Zero-copy Mmap substrate.",
            "4. Intelligence is now truly locally owned."
        ]
    },
    gemini: {
        title: "Gemini CLI Implementation",
        steps: [
            "1. Install Gemini CLI via Google Cloud SDK.",
            "2. Run <code>side connect gemini</code> to establish the local bridge.",
            "3. Use <code>gemini --context sidelith</code> for all project prompts.",
            "4. Your Google ecosystem is now hardened and siloed."
        ]
    }
};

function showIntegration(id) {
    const guide = document.getElementById('integration-guide');
    const data = integrations[id];

    if (!data) return;

    guide.style.display = 'block';
    guide.innerHTML = `
        <h3 style="color: var(--gold); margin-bottom: var(--spacing-sm);">${data.title}</h3>
        <ul style="list-style: none; text-align: left; max-width: 500px; margin: 0 auto;">
            ${data.steps.map(step => `<li style="margin-bottom: 8px;">${step}</li>`).join('')}
        </ul>
    `;

    // Highlight active card
    document.querySelectorAll('.integration-card').forEach(card => card.classList.remove('active'));
    event.currentTarget.classList.add('active');
}

function selectTier(tier) {
    const note = document.getElementById('tier-note');
    const command = document.getElementById('install-command');

    if (tier === 'node') {
        note.innerHTML = "You have selected the <strong>Sovereign Node</strong>. Installing with 500 SUs.";
        command.innerHTML = "curl -sSL https://sidelith.io/install.sh | sh --tier node";
    } else if (tier === 'mesh') {
        note.innerHTML = "Upgrading to <strong>Mesh Network</strong>. Subscription required after install.";
        command.innerHTML = "curl -sSL https://sidelith.io/install.sh | sh --tier mesh";
    } else {
        note.innerHTML = "Entering the <strong>Sovereign Network</strong>. Enterprise keys required.";
        command.innerHTML = "curl -sSL https://sidelith.io/install.sh | sh --tier elite";
    }
}
