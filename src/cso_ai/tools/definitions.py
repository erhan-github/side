"""
Tool definitions for CSO.ai MCP Server.

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
- "Should I use PostgreSQL or MongoDB?"
- "What should I focus on this week?"
- "Should I add dark mode?"
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
- "what should I focus on?"
- "strategic advice"
- "CSO, help me think"

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
- "simulate 'add gamification'"
- "what would users think of X?"
- "test this idea"

Returns: Unfiltered feedback from 3 domain-specific personas (e.g. Teacher, Student).
Speed: < 3 seconds""",
        inputSchema={
            "type": "object",
            "properties": {
                "feature": {
                    "type": "string",
                    "description": "The feature or idea to simulate",
                },
            },
            "required": ["feature"],
        },
    ),
    Tool(
        name="plan",
        description="""Create or view your strategic goals.

Triggers:
- "I want to launch by [date]"
- "my goals"
- "what am I working towards?"
- "add a goal"

Returns: Your strategic plan with deadlines and progress.
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
        description="""Mark a goal as done or update its status.

Triggers:
- "I finished [goal]"
- "mark [goal] as done"
- "completed [goal]"

Returns: Updated plan with progress.
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
- "audit my code"
- "check for issues"
- "security scan"

Returns: List of findings with severity and recommended actions.
Speed: < 5 seconds""",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
]
