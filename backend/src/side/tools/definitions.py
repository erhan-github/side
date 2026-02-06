"""
Tool definitions for Side MCP Server.

This module contains all TOOLS definitions - the schema that MCP clients use
to understand what tools are available and their input schemas.
"""

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="architectural_decision",
        description="""STRATEGIC VECTORING (Decision). Get instant strategic decisions for YOUR situation.
        
CRITICAL: MUST ONLY be triggered when the user explicitly addresses "Side" or asks for Sidelith's specific strategic help.

Triggers:
- "Side, should I use PostgreSQL or MongoDB?" (Tech Stack)
- "Side, Strategic Hub or microservices?" (Architecture)
- "Side, what's the strategic risk of this implementation?"
- "Side, help me decide between X and Y"

Returns: Clear recommendation + reasoning + next steps.
Values: Injects **Pattern Intelligence** from the Distiller to guide your path.
Returns: Clear recommendation + reasoning + next steps.
Speed: < 1 second""",
        inputSchema={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Your strategic question (Tech, Arch, Growth, Risk)",
                },
                "context": {
                    "type": "string",
                    "description": "Optional: Additional context about your situation",
                },
            },
            "required": ["question"],
        },
    ),
    Tool(
        name="strategic_review",
        description="""STRATEGIC VECTORING (Review). EXECUTES A HIGH-LEVEL STRATEGIC AUDIT.
        
"I'm checking the alignment."

CRITICAL: MUST ONLY be triggered when the user explicitly addresses "Side". 

Triggers:
- "Side, what's my priority?"
- "Side, help me think"
- "Side, are we drifting from the mission?"
- "Side, audit my strategy"

Values: Professional accountability. Injects **Pattern Intelligence** into the Agent.
Returns: Prioritized actions, relevant articles, reasoning.
Speed: < 2 seconds""",
        inputSchema={
            "type": "object",
            "properties": {
                "context": {
                    "type": "string",
                    "description": "Optional context about what you're working on",
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="plan",
        description="""STRATEGIC VECTORING (Planning). Create or view your strategic directives.

Triggers:
- "Side, log a goal: [goal]"
- "Side, what's my roadmap?"
- "Side, add a directive"

Returns: Your Hub-synced plan with deadlines and progress.
Speed: < 1 second""",
        inputSchema={
            "type": "object",
            "properties": {
                "goal": {
                    "type": "string",
                    "description": "New goal to add (optional)",
                },
                "due": {
                    "type": "string",
                    "description": "Due date for the goal (e.g. '2026-02-01')",
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="check",
        description="""STRATEGIC VECTORING (Alignment). Mark a directive as fulfilled.

Triggers:
- "Side, I finished [goal]"
- "Side, done with [goal]"
- "Side, completed [goal]"

Returns: Updated Hub with progress.
Speed: < 1 second""",
        inputSchema={
            "type": "object",
            "properties": {
                "goal": {
                    "type": "string",
                    "description": "Goal title or ID to mark as done",
                },
                "status": {
                    "type": "string",
                    "description": "New status (done, pending)",
                    "default": "done",
                },
            },
            "required": ["goal"],
        },
    ),
    Tool(
        name="run_audit",
        description="""FORENSIC PULSE. "I'm checking the vitals."
        
Scans your codebase via static analysis for security leaks or anti-patterns.

Triggers:
- "Side, audit my code"
- "Side, check for anti-patterns"
- "Side, run a forensic pulse"
- "Side, how's my codebase?"

Value: Not just a scan—it **extracts patterns** and **verifies documentation truth** into your local Pattern Store.
Returns: List of findings with severity and recommended actions. 
Speed: < 5 seconds""",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="reindex_dna",
        description="""CONTEXT DENSIFICATION. "I'm indexing the codebase architecture."
        
Multi-threaded indexing of your codebase architecture via tree-sitter.
        
Triggers:
- "Side, re-index the codebase architecture"
- "Side, update your architectural awareness"
- "Context densification"

Value: Moving from "text-matching" to "architectural awareness".
Returns: Stats on processed nodes.""",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Optional path to index (defaults to root)",
                },
            },
        },
    ),
    Tool(
        name="verify_fix",
        description="""Verify if a fix for a specific finding worked. Returns pass/fail.
        
        CRITICAL: Agent MUST call this tool after applying a fix to verify it worked.
        
        Triggers:
        - Agent self-check: "Did I fix the security issue?"
        - "Verify fix for SEC-001"
        
        Returns:
        - PASS: Issue resolved.
        - FAIL: Issue still present (with details).""",
        inputSchema={
            "type": "object",
            "properties": {
                "finding_type": {
                    "type": "string",
                    "description": "Type of finding to verify (e.g. 'Password Handling', 'File Length Limits')"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to check context for. If omitted, scans whole project."
                }
            },
            "required": ["finding_type"]
        },
    ),
    # Note: simulate_users is now an alias for simulate. Only expose one tool.
    Tool(
        name="welcome",
        description="""Day 1 setup - automatically run on first use.
        
Sets up Side and creates the Strategic Hub for a new project:
- Detects project name and stack
- Detects project name and stack
- Initializes the Sovereign Context state
- Runs baseline audit
- Stores initial health snapshot

This runs automatically when Side detects a new project.
Users can also run it manually with "side welcome" or "set up side".""",
        inputSchema={
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project root (defaults to current directory)",
                },
            },
        },
    ),
]
