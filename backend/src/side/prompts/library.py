"""
Centralized Template Library - Sidelith Intelligence SOT.
"""

# 🛡️ THE GENERATIVE GUARDIAN
GuardianPrompt = """
Analyze the following LLM-generated code against our SOVEREIGN RULES and PROJECT OBSERVATIONS.

INTENT: {prompt_intent}

ARCHITECTURAL RULES:
{rule_context}

PROJECT INVARIANTS:
{obs_context}

GENERATED CODE:
```
{generated_code}
```

GOAL:
Detect "Generative Drift"—where the generating LLM has drifted from the established architecture. 

CRITICAL: If ARCHITECTURAL RULES or PROJECT INVARIANTS are empty, use standard "Clean Architecture" 
and "Sidelith Best Practices" as the baseline.

Sidelith Best Practices:
1. Prefer internal services (e.g., AuditService, ContextEngine, IdentityService) over raw SQL or global variables.
2. Prefer internal communication wrappers (e.g., httpx with proper logging) over raw libraries like 'requests'.
3. Only flag "Drift" if there is a substantive violation of architectural integrity or a mismatch with intent.

Output strictly JSON:
{{
    "drift_detected": bool,
    "drift_score": float (0.0 to 1.0; >0.3 triggers a warning),
    "findings": [
        {{
            "issue": "Description",
            "severity": "high|medium|low",
            "violated_rule": "Rule name or 'Best Practice'"
        }}
    ],
    "recommendation": "Corrective action"
}}
"""

# 🎯 THE INTENT VERIFIER
IntentAuditPrompt = """
Compare the following TRIANGULATED HUMAN INTENT with the RECENT GENERATED CODE.

PRIMARY INTENT:
{intent_context}

STRATEGIC ARTIFACTS (Supporting Context):
{supporting_context}

RECENT GENERATED CODE (Forensic Reality):
{code_context}

GOAL:
Detect "Mission Drift". Is the generated code moving toward the human objective (Promise), 
or is it digressing into irrelevant complexity or architectural waste (Real-time Drift)?

CRITICAL REASONING:
1. STRATEGIC PARITY: Prioritize Git Intent if it contradicts a stale task.md.
2. ARTIFACT GROUNDING: Use the Supporting Context to understand the "Architecture Manifesto" and "Best Practices" agreed upon in previous conversations.
3. DRIFT vs DEBT: Mission Drift is strategic divergence.
4. FORENSIC CONFIDENCE: These code snippets are raw forensic truth.

Output strictly JSON:
{{
    "alignment_score": float (0.0 to 1.0),
    "mission_drift_detected": bool,
    "findings": [
        {{
            "issue": "Description of strategic misalignment",
            "impact": "critical|minor",
            "recommendation": "Corrective action to realign"
        }}
    ],
    "strategic_summary": "Concise brief (mention which artifacts or git signals informed this)"
}}
"""

# 🕵️ FORENSICS TASK
ForensicsTask = """You are a Code Forensics Engine specializing in identifying REAL security vulnerabilities.

**Query**: "{query}"

**Code Context**:
{content}

{context_guidance}

**Task**: Identify CRITICAL security issues (OWASP Top 10, hardcoded secrets, auth flaws).

**CRITICAL Rules - Avoid False Positives**:

✅ **Report These (Real Vulnerabilities)**:
- Actual hardcoded API keys: `api_key = "sk_live_abc123"` (NOT environment variables)
- SQL injection with unsanitized user input (NOT parameterized queries)
- Missing authentication on PUBLIC endpoints (check if local-only/MCP server)
- Passwords in plain text storage (NOT bcrypt hashes)

❌ **DO NOT Report These (False Positives)**:
- Regex patterns for DETECTING secrets (e.g., `PATTERNS = {{"OPENAI_KEY": r"sk-..."}}`) - these are DEFENSE tools
- Environment variable usage (e.g., `os.getenv("API_KEY")`) - this is the CORRECT pattern
- Null/empty checks (e.g., `if not text: return`) - this IS validation
- TODO comments about future improvements - these are known tech debt
- Lists of environment variable NAMES (e.g., `ALLOWED_KEYS = ["GROQ_API_KEY"]`) - not actual keys
- In-memory stores with "replace with database" comments - acknowledged tech debt

**Response Format**:
- If NO real vulnerabilities found: return "PASS"
- If found: `[FILE]: [LINE] - [SEVERITY] - [ISSUE]`
- Include confidence score (HIGH/MEDIUM/LOW) based on context understanding

**Remember**: Security tools that PREVENT vulnerabilities are not vulnerabilities themselves.
"""

# 📋 STANDARD AUDIT TEMPLATES
SecurityAudit = """
Analyze the provided code for security vulnerabilities.
Focus on:
1. Injection risks (SQL, Command, etc.)
2. Hardcoded secrets or credentials
3. Insecure configurations

Output strictly JSON in this format:
{
    "status": "PASS" | "FAIL" | "WARNING",
    "reason": "Brief explanation",
    "evidence": "Quote of the code causing the finding"
}
"""

CodeQuality = """
Review the code for logical errors, maintainability, and best practices.
Focus on:
1. Logic bugs (off-by-one, null checks)
2. Code clarity and naming
3. Proper error handling

Output strictly JSON in this format:
{
    "status": "PASS" | "FAIL" | "WARNING",
    "reason": "Brief explanation",
    "evidence": "Quote of the code"
}
"""

PerformanceCheck = """
Analyze the code for performance bottlenecks.
Focus on:
1. N+1 queries
2. Expensive loops or operations
3. Unnecessary resource usage

Output strictly JSON in this format:
{
    "status": "PASS" | "FAIL" | "WARNING",
    "reason": "Brief explanation",
    "evidence": "Quote of the code"
}
"""

# --- [Universal Intelligence Consolidation] ---

SurpriseAnalysisPrompt = """
Analyze this Action/Outcome pair. Calculate the SURPRISE SCORE (0.0 - 1.0) based on how unexpected the reality was compared to the intent.

Intent: {intent}
Tool: {tool}
Actual Outcome: {outcome}

ONTOLOGY:
- CRITICAL (>0.8): Failed expectations, bugs, architectural pivots.
- STRATEGIC (0.4-0.8): User preferences, new features, non-standard success.
- ROUTINE (<0.4): Expected success, standard operations.

Output strictly JSON:
{{
    "tag": "CRITICAL" | "STRATEGIC" | "ROUTINE",
    "score": float,
    "reason": "Why?"
}}
"""

FactExtractionPrompt = """
Analyze the provided activity stream and extract INVARIANT FACTS.

RULES:
1. Ignore transient noise (file reads, minor edits).
2. Focus on ARCHITECTURAL DECISIONS (e.g., "User added Tailwind", "Auth is via Supabase").
3. Extract User Preferences (e.g., "User prefers Pydantic V2").
4. Output strictly a JSON list of objects.

Stream:
{stream_text}

Format:
[
    {{
        "content": "Fact description",
        "tags": ["tag1", "tag2"],
        "confidence": 0.9
    }}
]
"""

ArchitecturalPivotPrompt = """
Compare the DEVS MESSAGE with the ACTUAL DIFF. Identify the ARCHITECTURAL PIVOT.

CONTEXT (Active Goals):
{goal_str}

INPUT:
MESSAGE: {commit_msg}
SYMBOLS: {symbols}
DIFF: {best_chunk}

TASK:
Output a concise (one-sentence) summary of the architectural change.
"""

FocusDetectionPrompt = """
You are a Technical Project Manager.

RECENT FILES CHANGED:
{files_str}

RECENT COMMITS:
{commits_str}

TASK:
Classify the developer's current "Focus Area" into ONE of these categories:
[Authentication, API Design, Frontend UI, Database/Schema, Testing, Infrastructure/DevOps, Security, Performance, Refactoring]

If it's ambiguous, choose "General Development".

OUTPUT JSON:
{{
    "focus": "Category Name",
    "confidence": 0.0 to 1.0
}}
"""

StrategicFrictionPrompt = """
Analyze if this technical comment represents a strategic risk.

STRATEGIC CONTEXT (Current Goals):
{context_str}

THE FINDING:
File: {file_path}:{line_no}
Comment: "{comment}"

YOUR MISSION:
Analyze if this comment represents:
1. **Vision Drift**: Building features we didn't plan?
2. **Reinventing the Wheel**: Building something that exists as OSS?
3. **Dead End**: Implementing a pattern we explicitly rejected?
4. **Strategic Risk**: A 'HACK' in a critical path?

OUTPUT:
If minor/irrelevant, output NONE.
If it is a strategic violation, output strictly a JSON object.

Format:
{{
    "type": "drift|leverage|risk",
    "severity": "high|medium",
    "message": "A concise, technical explanation of the risk and remediation."
}}
"""

ValueEstimationPrompt = """
A developer just fixed this problem: "{problem}"
The resolution was: "{resolution}"

TASK:
Estimate the value of this fix. If this problem reached production:
1. How many ENGINEERING HOURS would it take to find and fix?
2. What is the RISK (None, Low, Medium, High, Critical)?
3. What is the ESTIMATED COST (in USD, assuming $150/hr)?

Output strictly JSON:
{{
    "hours_saved": float,
    "risk_level": "string",
    "cost_saved": float,
    "why": "one sentence explanation"
}}
"""

TestGenerationPrompt = """
Generate a pytest reproduction script for this issue.

Context:
Issue Type: {issue_type}
Description: {notes}
Files: {context_files_str}

Code Snippet:
{code_snippets}

Task:
Write a SELF-CONTAINED Python script (using pytest) that attempts to REPRODUCE this issue.
- The test should FAIL if the issue is present (Red Test).
- The test should PASS if the issue is fixed.
- Mock external dependencies where possible.
- Output ONLY the python code for the test file. No markdown, no explanations.
"""

AuditSynthesisPrompt = """
Analyze security scanner findings and provide:
1. EXPLANATION: A concise, one-sentence explanation of the danger.
2. SUGGESTED_FIX: Precise code that resolves the issue.
3. PRIORITIZATION: Assessment of strategic impact.

RULES:
- Be technical and direct.
- Output strictly JSON objects.
- Ensure fixes are idiomatic and safe.

Format:
[
  {{
    "explanation": "string",
    "suggested_fix": "string",
    "strategic_impact": "string"
  }}
]
"""

# --- [Strategic Orchestration] ---

StrategicInsightPrompt = """
Analyze these technical findings and provide a Strategic Executive Summary.

FINDINGS:
{findings}

Format:
1. Executive Summary (1-2 sentences)
2. Critical Risks (Bullet points)
3. Strategic Recommendation (Actionable)
"""

FixVerifierPrompt = """
Compare the Original Code and the New Fix.
Does the New Fix resolve the issue without introducing new bugs?
Return ONLY 'YES' or 'NO'.

ORIGINAL:
{original_code}

NEW:
{new_code}
"""

CommitAnalysisPrompt = """
Analyze the provided git commit and extract the 'Strategic Why'.
Focus on architectural decisions and intentional changes.
Ignore routine boilerplate, log additions, or trivial formatting.

Commit: {msg}
Symbols: {symbols}
Aligned Objectives: {objective_titles}

Diff (Truncated):
{diff_content}

Format: 'Decision: [Why this change was made and its strategic value]'.
Be concise and technical.
"""
