"""
Tool definitions for Side MCP Server.

This module contains all TOOLS definitions - the schema that MCP clients use
to understand what tools are available and their input schemas.
"""

from mcp.types import Tool

TOOLS: list[Tool] = [
    Tool(
        name="architectural_decision",
        description="""Get instant strategic decisions for YOUR situation.
        
CRITICAL: Do NOT call this for syntax help, debugging, or simple code generation. ONLY call for high-stakes architectural decisions.

Triggers:
- "Side, should I use PostgreSQL or MongoDB?"
- "Side, help me decide"
- "What do you think about X?"
- "Monolith or microservices?"

Returns: Clear recommendation + reasoning + next steps.
Speed: < 1 second

NOT generic advice - based on YOUR codebase, team, and stage.""",
        inputSchema={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Your strategic question",
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
        description="""EXECUTES A HIGH-LEVEL STRATEGIC AUDIT. Expensive operation. Use only for major milestone checks.

CRITICAL: Do NOT call for daily status updates or minor questions.

Triggers:
- "Side, what's my priority?"
- "Side, help me think"
- "What should I focus on?"
- "Audit my strategy"

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
        name="simulate",
        description="""Run your idea past Virtual Users (Personas).

CRITICAL: Use ONLY when a specific feature or idea is proposed. Do NOT use for general chat.

Triggers:
- "Side, test this idea"
- "What would users think of X?"
- "Would developers like this?"
- "Focus group for my landing page"

Returns: Unfiltered feedback from 3 domain-specific personas (e.g. Teacher, Developer).
Speed: < 3 seconds""",
        inputSchema={
            "type": "object",
            "properties": {
                "feature": {
                    "type": "string",
                    "description": "The feature or idea to simulate",
                },
                "target_audience": {
                    "type": "string",
                    "enum": ["teachers", "developers", "general", "designers"],
                    "description": "Who are we testing with? (default: general)",
                },
                "content": {
                    "type": "string",
                    "description": "The text content to test (Landing Page, Feature, Idea)",
                },
                "content_type": {
                    "type": "string",
                    "description": "What is this? (e.g. 'Landing Page', 'Email Subject')",
                },
            },
            "required": [],
        },
    ),
    Tool(
        name="plan",
        description="""Create or view your strategic directives.

Triggers:
- "Side, log a goal: [goal]"
- "Side, what's my roadmap?"
- "My goals"
- "Add a directive"

Returns: Your Monolith-synced plan with deadlines and progress.
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
        description="""Mark a directive as fulfilled.

Triggers:
- "Side, I finished [goal]"
- "Side, done with [goal]"
- "Completed [goal]"
- "Check off [goal]"

Returns: Updated Monolith with progress.
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
        description="""Run a forensic audit on your codebase.

Triggers:
- "Side, audit my code"
- "Side, how's my codebase?"
- "Check for issues"
- "Security scan"

Returns: List of findings with severity and recommended actions. Updates the Monolith.
Speed: < 5 seconds""",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    # Note: simulate_users is now an alias for simulate. Only expose one tool.
    Tool(
        name="welcome",
        description="""Day 1 setup - automatically run on first use.
        
Sets up Side for a new project:
- Detects project name and stack
- Creates .side/plan.md
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
