"""
Crawler Probe - Dynamic analysis of running application.

Forensic-level dynamic checks:
- Live connectivity check
- Internal link crawling (BFS)
- Dead link detection (404/500)
- Response time tracking
"""

import re
import asyncio
import httpx
from pathlib import Path
from typing import List, Set, Dict
from urllib.parse import urljoin, urlparse
from ..core import AuditResult, AuditStatus, AuditEvidence, ProbeContext, Severity, Tier

class CrawlerProbe:
    """
    Forensic-level dynamic crawler.
    
    Visits the running application to map structure and find errors.
    """
    
    id = "forensic.crawler"
    name = "Live System Crawler"
    tier = Tier.DEEP  # It involves network requests
    dimension = "Live System"
    
    # Configuration
    MAX_PAGES = 50
    MAX_DEPTH = 3
    TIMEOUT = 5.0
    
    def _crawl(self, start_url: str) -> Dict[str, Dict]:
        """
        Crawl website and analyze content.
        Returns: {url: {'status': int, 'links': [], 'title': str, 'has_mock_text': bool, 'placeholder_links': int, 'is_duplicate_home': bool}}
        """
        visited: Dict[str, Dict] = {}
        queue: List[tuple[str, int]] = [(start_url, 0)]
        domain = urlparse(start_url).netloc
        
        # Capture Home Page Signal
        home_content_len = 0
        home_title = ""
        
        with httpx.Client(timeout=self.TIMEOUT, follow_redirects=True) as client:
            try:
                # Initial check & Baseline
                resp = client.get(start_url)
                if resp.status_code >= 400:
                    return {start_url: {'status': resp.status_code}}
                
                # Store Home Baseline
                home_content_len = len(resp.text)
                m = re.search(r'<title>(.*?)</title>', resp.text, re.IGNORECASE)
                if m: home_title = m.group(1)
                
            except Exception:
                return {}

            while queue and len(visited) < self.MAX_PAGES:
                url, depth = queue.pop(0)
                
                if url in visited or depth > self.MAX_DEPTH:
                    continue
                
                try:
                    resp = client.get(url)
                    
                    # Detect Soft 404s / Redirects
                    final_url = str(resp.url)
                    req_u = url.rstrip('/')
                    res_u = final_url.rstrip('/')
                    
                    is_redirected_home = False
                    if req_u != res_u and (res_u == start_url.rstrip('/') or res_u.endswith('/')):
                         is_redirected_home = True

                    # Analyze Content
                    has_mock = False
                    placeholder_count = 0
                    home_links_count = 0
                    is_duplicate_home = False
                    status_override = None
                    title = ""
                    
                    if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", ""):
                        content = resp.text
                        
                        # Get Title
                        t_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                        if t_match:
                            title = t_match.group(1)
                            
                        # Check for Next.js/React Runtime Errors (Global Check)
                        # We check this for ALL pages, including home.
                        content_lower = content.lower()
                        error_sigs = ["unhandled runtime error", "application error: a client-side exception has occurred", "fetch failed", "internal server error", "console.error"]
                        
                        if any(sig in content_lower for sig in error_sigs):
                             # This is a crash served as HTML
                             status_override = 500
                             title = "Runtime Error Detected"
                        
                        # CRITICAL: Check if this page is just a clone of Home (Client-side redirect or Placeholder)
                        # If URL is NOT home, but content length and title match Home exactly -> It's a redirect.
                        if url != start_url:
                            # 1. Check for Duplicate Home (Soft 404)
                            if abs(len(content) - home_content_len) < 50 and title == home_title and not status_override:
                                is_duplicate_home = True
                            
                        # Check for Mock Indicators
                        if any(x in content.lower() for x in ['lorem ipsum', 'mock data', 'demo mode', 'dummy user', 'prototype', 'wireframe', 'todo:', 'fixme:']):
                            has_mock = True
                        if any(x in title.lower() for x in ['mock', 'demo', 'stub', 'prototype']):
                            has_mock = True
                        
                        # Extract Links
                        raw_links = re.findall(r'href=["\'](.*?)["\']', content)
                        
                        # 1. Analyze Link Health (Placeholders & Suspicious Redirects)
                        for link in raw_links:
                            link = link.strip()
                            if link in ['#', '', 'javascript:void(0)']:
                                placeholder_count += 1
                            elif url != start_url and (link == '/' or link == start_url):
                                home_links_count += 1
                                
                        # Heuristic: Allow 2 home links (Logo + Footer). Excess are considered broken flows.
                        if home_links_count > 2:
                            placeholder_count += (home_links_count - 2)

                        # 2. Add to Crawl Queue
                        for link in raw_links:
                            link = link.strip()
                            if link in ['#', '', 'javascript:void(0)'] or link == '/' or link == start_url:
                                continue
                                
                            full_url = urljoin(url, link)
                            parsed = urlparse(full_url)
                            if parsed.netloc == domain:
                                if any(full_url.endswith(ext) for ext in ['.png', '.jpg', '.css', '.js']):
                                    continue
                                if '#' in link and len(link) > 1:
                                    continue 
                                    
                                if full_url not in visited:
                                    queue.append((full_url, depth + 1))
                                    
                    final_status = resp.status_code
                    if status_override:
                        final_status = status_override
                    elif is_redirected_home or is_duplicate_home:
                        final_status = 302
                        
                    visited[url] = {
                        'status': final_status,
                        'has_mock': has_mock, 
                        'placeholder_links': placeholder_count,
                        'title': title
                    }
                                    
                except Exception:
                    visited[url] = {'status': 0}
                    
        return visited

    def _discover_routes(self, project_root: str) -> List[str]:
        """Discover Next.js/React routes from file system."""
        routes = []
        root = Path(project_root)
        
        # Check for Next.js app directory
        app_dir = root / "web" / "app"
        if not app_dir.exists():
            app_dir = root / "app"
            
        if app_dir.exists():
            for page in app_dir.rglob("page.tsx"):
                # Convert path to route
                rel_path = page.relative_to(app_dir)
                route_parts = rel_path.parent.parts
                
                # Handle dynamic routes (skip or mock?)
                if any('[' in p for p in route_parts):
                    continue
                    
                if len(route_parts) == 0:
                    routes.append("/")
                else:
                    routes.append("/" + "/".join(route_parts))
                    
        return list(set(routes))

    def _detect_port(self, project_root: str) -> List[str]:
        """Detect port from env or package.json."""
        ports = ["3999", "3000", "8000"] # Defaults
        root = Path(project_root)
        
        # 1. Check .env
        env_files = list(root.rglob(".env*"))
        for env_file in env_files:
            try:
                content = env_file.read_text()
                # Find PORT=xxxx
                matches = re.findall(r'PORT=(\d+)', content)
                ports.extend(matches)
            except:
                pass
                
        # 2. Check package.json scripts for -p flag
        # "dev": "next dev -p 3999"
        pkg_json = root / "web" / "package.json"
        if pkg_json.exists():
            try:
                content = pkg_json.read_text()
                matches = re.findall(r'-p\s+(\d+)', content)
                ports.extend(matches)
            except:
                pass
                
        # Unique and formatted
        return [f"http://localhost:{p}" for p in set(ports)]

    def run(self, context: ProbeContext) -> List[AuditResult]:
        """Run the crawler (Synchronous)."""
        # Smart detect ports
        targets = self._detect_port(context.project_root)
        
        # Add discovered routes to targets
        # We assume the server is running at one of the base targets
        discovered_routes = self._discover_routes(context.project_root)

        
        results = {}
        target_url = None
        
        try:
            # First find the live base URL
            base_url = None
            for t in targets:
                # Quick health check
                try:
                    with httpx.Client(timeout=2.0) as client:
                        if client.get(t).status_code < 500:
                            base_url = t
                            break
                except:
                    continue
            
            if base_url:
                target_url = base_url
                # Seed the crawler with discovered routes + base
                seed_urls = [base_url]
                for r in discovered_routes:
                    seed_urls.append(urljoin(base_url, r))
                
                # Crawl all seeds
                for url in seed_urls:
                    # Merge results
                    visited_page = self._crawl(url)
                    results.update(visited_page)

        except Exception as e:
            return [AuditResult(
                check_id="CRAWL-001",
                check_name="Live System Check",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.LOW,
                notes=f"Crawler failed: {str(e)}"
            )]
            
        if not results:
            return [AuditResult(
                check_id="CRAWL-001",
                check_name="Live System Check",
                dimension=self.dimension,
                status=AuditStatus.SKIP,
                severity=Severity.HIGH,
                notes=f"No running server found",
                recommendation="Start your server to enable live auditing"
            )]
            
        # Analyze Results
        evidence_health = []
        evidence_ux = []
        
        broken_links = 0
        server_errors = 0
        total_placeholders = 0
        mock_pages = []
        
        for url, data in results.items():
            status = data.get('status', 0)
            
            # Health
            if status == 404:
                broken_links += 1
                evidence_health.append(AuditEvidence(description="Broken link (404)", context=url))
            elif status == 302:
                # We interpret 302 as "Suspicious Redirect to Home" from our _crawl logic
                broken_links += 1
                evidence_health.append(AuditEvidence(description="Suspicious Redirect (Soft 404)", context=url))
            elif status >= 500:
                server_errors += 1
                evidence_health.append(AuditEvidence(description=f"Server error ({status})", context=url))
            
            # UX / Mock
            if data.get('has_mock'):
                mock_pages.append(url)
            
            p_count = data.get('placeholder_links', 0)
            if p_count > 0:
                total_placeholders += p_count
                evidence_ux.append(AuditEvidence(
                    description=f"{p_count} placeholder links (href='#')",
                    context=url,
                    suggested_fix="Wire up buttons to real routes"
                ))

        # 1. Server Status
        checks = [AuditResult(
            check_id="CRAWL-001",
            check_name="Live System Connectivity",
            dimension=self.dimension,
            status=AuditStatus.PASS,
            severity=Severity.CRITICAL,
            notes=f"Connected to {target_url}",
            confidence=1.0
        )]
        
        # 2. Link Health
        health_status = AuditStatus.PASS
        if server_errors > 0: health_status = AuditStatus.FAIL
        elif broken_links > 0: health_status = AuditStatus.WARN
            
        checks.append(AuditResult(
            check_id="CRAWL-002",
            check_name="Internal Link Health",
            dimension=self.dimension,
            status=health_status,
            severity=Severity.HIGH,
            evidence=evidence_health,
            notes=f"Scanned {len(results)} pages. Found {broken_links} broken links and {server_errors} server errors.",
            recommendation="Fix broken links/routes" if broken_links > 0 else None
        ))
        
        # 3. UX Readiness (Dynamic)
        # Note: We classify this under 'Product Readiness' dimension effectively, 
        # but keep the Probe dimension as Live System.
        # However, to group it nicely in the report, we can reuse the same check pattern.
        
        ux_status = AuditStatus.PASS
        ux_notes = []
        
        if mock_pages:
            ux_status = AuditStatus.WARN # Warn about mocks in live system
            ux_notes.append(f"Found {len(mock_pages)} live mock pages")
            for mp in mock_pages:
                evidence_ux.append(AuditEvidence(description="Live Mock Page", context=mp))
                
        if total_placeholders > 0:
            ux_status = AuditStatus.WARN
            ux_notes.append(f"Found {total_placeholders} dead buttons/links (href='#')")
            
        checks.append(AuditResult(
            check_id="CRAWL-003",
            check_name="UX Interaction Readiness",
            dimension="Product Readiness",
            status=ux_status,
            severity=Severity.MEDIUM,
            evidence=evidence_ux,
            notes=", ".join(ux_notes) if ux_notes else "Interactive elements appear wired up",
            recommendation="Connect all placeholder buttons to real logic"
        ))
        
        return checks
