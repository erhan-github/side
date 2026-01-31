import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from side.tools.recursive_utils import partition, peek, grep, chunk_list
from side.llm.client import LLMClient
from side.intel.forensic_allowlist import allowlist

logger = logging.getLogger(__name__)

class ForensicsTool:
    """
    Implements "Deep Audit" capabilities using Recursive Language Models (RLMs).
    Instead of reading the whole codebase, we:
    1. Filter relevant files (grep/find).
    2. Partition them into chunks.
    3. Peek at headers.
    4. Recursively analyze.
    """

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.llm = LLMClient()

    async def scan_codebase(self, query: str) -> str:
        """
        Recursively scan the codebase for a specific forensic query.
        Example: "Find all hardcoded secrets" or "Check ensuring strict type adherence"
        """
        # 1. Discovery Phase: Find relevant files
        all_files = self._find_files()
        
        # 2. Partition Strategy
        # If too many files, we filter first.
        # For this v1, we'll grep for keywords related to the query if accessible,
        # otherwise we take a sampling approach.
        
        # Simple heuristic: Grep for suspicious patterns if query mentions secrets
        suspicious_files = []
        keywords = ["secret", "key", "token", "password", "auth", "credential"]
             
        # Construct grep command (case insensitive, recursive, list filenames)
        # We use subprocess directly for speed
        import subprocess
        try:
            cmd = ["grep", "-irl", "-E", "|".join(keywords), str(self.project_path)]
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                found_files = []
                for line in result.stdout.strip().splitlines():
                    if line:
                        path = Path(line)
                        if path in all_files: # Only include if it passed the base filter
                            found_files.append(path)
                
                if found_files:
                    logger.info(f"🔎 [FILTER] Grep reduced scan from {len(all_files)} to {len(found_files)} high-risk files.")
                    suspicious_files = found_files
        except Exception as e:
            logger.warning(f"Grep filter failed, falling back to full scan: {e}")

        if suspicious_files:
            targets = suspicious_files
        else:
            targets = all_files

        # 3. Recursive Analysis
        # We split the file list into chunks of 5 files to prevent context overflow
        chunks = chunk_list(targets, size=5)
        
        findings = []
        logger.info(f"🔎 [FORENSICS] Scanning {len(all_files)} files in {len(chunks)} chunks...")

        for chunk in chunks[:10]: # Limit to top 50 files for speed in V1
            chunk_content = ""
            for file_path in chunk:
                try:
                    content = file_path.read_text(errors='ignore')
                    # Peek only first 500 lines to save tokens
                    preview = peek(content, lines=500) 
                    chunk_content += f"\n--- File: {file_path.relative_to(self.project_path)} ---\n{preview}\n"
                except Exception:
                    continue
            
            # Analyze this chunk
            if chunk_content:
                finding = await self._analyze_chunk(chunk_content, query)
                if finding:
                    findings.append(finding)
        
        # 4. Synthesize Results
        report = self._synthesize_report(findings, query)
        return report, findings

    def _find_files(self, patterns: List[str] = None) -> List[Path]:
        """Return a list of source code files."""
        # Standard excludes
        excludes = {'.git', 'node_modules', '__pycache__', 'venv', 'env', '.DS_Store'}
        files = []
        for root, dirs, filenames in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in excludes]
            for name in filenames:
                if name.endswith(('.py', '.js', '.ts', '.tsx', '.go', '.rs', '.md')):
                    files.append(Path(root) / name)
        return files

    async def _analyze_chunk(self, content: str, query: str) -> str:
        """Ask LLM to find issues in a single chunk with context-aware guidance."""
        
        # Extract file paths from content to get context guidance
        context_guidance = self._extract_context_guidance(content)
        
        prompt = f"""You are a Code Forensics Engine specializing in identifying REAL security vulnerabilities.

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
        try:
            response = await self.llm.complete_async(
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are an expert security auditor who distinguishes real vulnerabilities from false positives.",
                temperature=0.0
            )
            if "PASS" in response:
                return None
            
            # Phase 2: Verification - Check against allowlist
            verified_response = self._verify_findings(response, content)
            return verified_response if verified_response else None
            
        except Exception as e:
            logger.error(f"❌ LLM Audit Failed for chunk: {e}")
            return None
    
    def _extract_context_guidance(self, content: str) -> str:
        """Extract file paths and generate context guidance."""
        import re
        file_matches = re.findall(r'--- File: ([^\s]+) ---', content)
        
        if not file_matches:
            return ""
        
        guidance_parts = []
        for file_path in file_matches[:3]:  # Limit to first 3 files
            guidance = allowlist.get_context_guidance(file_path)
            if guidance:
                guidance_parts.append(f"\n**Context for {file_path}**:\n{guidance}")
        
        return "\n".join(guidance_parts) if guidance_parts else ""
    
    def _verify_findings(self, findings_text: str, content: str) -> Optional[str]:
        """Verify findings against allowlist to eliminate false positives."""
        if not findings_text or findings_text.strip() == "PASS":
            return None
        
        import re
        # Parse findings in format: [FILE]: [LINE] - [ISSUE]
        finding_pattern = r'\[([^\]]+)\]:\s*(\d+)\s*-\s*(.+)'
        matches = re.findall(finding_pattern, findings_text)
        
        verified_findings = []
        filtered_count = 0
        
        for file_path, line_str, issue_description in matches:
            try:
                line_num = int(line_str)
                
                # Extract code snippet from content
                code_snippet = self._extract_code_snippet(content, file_path, line_num)
                
                # Check allowlist
                safe_check = allowlist.check_safe_pattern(file_path, line_num, code_snippet)
                
                if safe_check:
                    logger.info(f"🛡️ [FILTERED] False positive in {file_path}:{line_num} - {safe_check['reason']}")
                    filtered_count += 1
                    continue
                
                # This finding passed verification
                verified_findings.append(f"[{file_path}]: {line_num} - {issue_description}")
            except Exception as e:
                logger.debug(f"Error parsing finding: {e}")
                # If we can't parse it, include it to be safe
                verified_findings.append(f"[{file_path}]: {line_str} - {issue_description}")
        
        if filtered_count > 0:
            logger.info(f"✅ [ALLOWLIST] Filtered {filtered_count} false positives")
        
        return "\n".join(verified_findings) if verified_findings else None
    
    def _extract_code_snippet(self, content: str, file_path: str, line_num: int, context_lines: int = 3) -> str:
        """Extract code snippet around a specific line from content."""
        import re
        
        # Find the file section in content
        file_marker = f"--- File: {file_path} ---"
        if file_marker not in content:
            return ""
        
        # Extract content for this file
        file_start = content.find(file_marker)
        next_file = content.find("--- File:", file_start + len(file_marker))
        file_content = content[file_start:next_file] if next_file != -1 else content[file_start:]
        
        # Get lines around the target
        lines = file_content.split('\n')
        if line_num < len(lines):
            start = max(0, line_num - context_lines - 1)
            end = min(len(lines), line_num + context_lines)
            return '\n'.join(lines[start:end])
        
        return file_content[:500]  # Fallback to first 500 chars

    def _synthesize_report(self, findings: List[str], query: str) -> str:
        if not findings:
            return f"✅ **Forensics Clean:** No issues found for '{query}'."
        
        issue_count = len(findings)
        
        # 1. THE HOOK
        report = [f"🕵️ **Forensics Alert: {issue_count} Issues Detected**"]
        report.append("")
        
        # 2. THE EVIDENCE
        report.append("**Key Findings:**")
        # Extract meaningful summaries from findings if possible, or just list top 3
        # Findings are raw strings "[FILE]: [LINE] - [ISSUE]"
        for finding in findings[:5]: 
             # Cleanup finding string to be bullet point
             clean_finding = finding.strip().replace("\n", " ")
             report.append(f"*   {clean_finding[:100]}...")
        
        if issue_count > 5:
            report.append(f"*   ... and {issue_count - 5} more.")
        report.append("")
        
        # 3. THE PROPOSAL (The Button)
        # We propose a Plan to fix these.
        report.append(f"> **Side Proposes Action:** `plan`")
        report.append(f"> *Run this to create a remediation plan.*")
        
        # Tool Proposal Signal
        report.append(f"tool_code: call_tool('plan', {{'goal': 'Remediate {issue_count} forensic issues found in {query}', 'due': 'today'}})")
        
        return "\n".join(report)
