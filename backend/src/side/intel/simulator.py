"""
Side Simulator - Virtual User Testing.

Generates synthetic personas based on the project's domain and simulates their feedback.
Zero storage - personas are hallucinated on flight based on archetypes.

Usage:
    sim = Simulator()
    feedback = await sim.simulate_feedback("Add a dark mode", domain="EdTech")
"""

import logging
import asyncio
from dataclasses import dataclass
from side.storage.simple_db import SimplifiedDatabase
from side.intel.strategist import Strategist
from side.intel.signals import SignalAggregator
from pathlib import Path
from typing import Any, List, Optional

logger = logging.getLogger("side.intel.simulator")

@dataclass
class Persona:
    name: str
    role: str
    obsessions: str
    category: str  # 'Critic', 'User', 'Hype', 'Maker'

class Simulator:
    """
    Retrieval Augmented Persona (RAP) Engine.
    
    Simulates user feedback by injecting LIVE market trends into 32 distinct personas.
    Grounds hallucination in actual industry reality (e.g. "DeepSeek is cheaper", "Vercel is expensive").
    """
    
    # -------------------------------------------------------------------------
    # The Cast: 32 Distinct Voices (The "Secret Sauce")
    # -------------------------------------------------------------------------
    PERSONAS = [
        # --- THE CRITICS (Hard to please) ---
        Persona("Angry Senior Dev", "Senior Backend Engineer", "Clean code, no magic, hates 'AI wrappers'", "Critic"),
        Persona("The Security Paranoid", "InfoSec Lead", "Data residency, SOC2, PII leaks, zero trust", "Critic"),
        Persona("The Performance OCD", "Systems Architect", "Latency distributions, bundle size, memory leaks", "Critic"),
        Persona("The VC Analyst", "Series A Associate", "Moats, retention, unit economics, TAM", "Critic"),
        Persona("The Procurement Blocker", "IT Buyer", "Compliance, SSO, SLA, vendor lock-in", "Critic"),
        Persona("The Accessibility Advocate", "Frontend Lead", "WCAG 2.1, screen readers, semantic HTML", "Critic"),
        Persona("The Legacy Keeper", "Mainframe Maintainer", "Stability, backward compatibility, 10-year support", "Critic"),
        Persona("The Open Source Purist", "FOSS Contributor", "MIT license, vendor neutrality, self-hosting", "Critic"),

        # --- THE USERS (The actual people) ---
        Persona("The Tired Mom", "Remote PM", "Efficiency, fewer clicks, dark mode (migraine friendly)", "User"),
        Persona("The Gen Z Intern", "Junior Dev", "Vibe coding, Discord integration, fast onboarding", "User"),
        Persona("The Enterprise Drone", "BigCorp Employee", "Microsoft Teams integration, Excel export, apathy", "User"),
        Persona("The Mobile Warrior", "Field Sales", "Touch targets, offline mode, battery usage", "User"),
        Persona("Grandma Betty", "Non-Technical User", "Big fonts, clear buttons, fear of breaking things", "User"),
        Persona("Dr. House", "Specialist Power User", "Keyboard shortcuts, information density, speed", "User"),
        Persona("The Student", "CS Undergrad", "Free tier, cheat sheets, homework help", "User"),
        Persona("The Manager", "Engineering Manager", "Velocity metrics, JIRA sync, team oversight", "User"),

        # --- THE HYPE CYCLE (Trend chasers) ---
        Persona("The Rust Evangelist", "Systems Engineer", "Memory safety, rewrite it in Rust, Cargo", "Hype"),
        Persona("The AI Doomer", "Ethicist", "Safety guardrails, alignment, job displacement", "Hype"),
        Persona("The Crypto Bro", "Web3 Founder", "Decentralization, tokenomics, censorship resistance", "Hype"),
        Persona("The JS Framework Hopper", "Fullstack Dev", "Next.js 15, RSC, Bun, latest npm package", "Hype"),
        Persona("The AGI Accelerationist", "AI Researcher", "Agents, autonomy, recursive self-improvement", "Hype"),
        Persona("The No-Code Wizard", "Citizen Developer", "Zapier, Airtable, Bubble, automation", "Hype"),
        Persona("The VR Enthusiast", "Spatial Computing Dev", "Immersion, spatial UI, hand tracking", "Hype"),
        Persona("The Growth Hacker", "Marketing Lead", "Virality, SEO, social proof, gamification", "Hype"),

        # --- THE MAKERS (Builders) ---
        Persona("The Indie Hacker", "Bootstrapper", "Time to market, stripe integration, low overhead", "Maker"),
        Persona("The DevOps Ninja", "SRE", "Terraform, Kubernetes, CI/CD pipelines", "Maker"),
        Persona("The Data Scientist", "ML Engineer", "Python, Jupyter, reproducibility, GPU cost", "Maker"),
        Persona("The UX Purist", "Product Designer", "White space, typography, micro-interactions", "Maker"),
        Persona("The API Architect", "Backend Lead", "REST vs GraphQL, idempotency, rate limiting", "Maker"),
        Persona("The Testing Guru", "QA Lead", "E2E tests, coverage assertions, flake detection", "Maker"),
        # --- THE EXECUTIVES (The Money) ---
        Persona("The CFO", "Chief Financial Officer", "OpEx reduction, vendor consolidation, ROI", "Critic"),
        Persona("The CTO", "Chief Technology Officer", "Tech debt, hiring velocity, bus factor", "Critic"),
        Persona("The Compliance Officer", "Legal", "GDPR, HIPAA, SOC2, lawsuits", "Critic"),
        Persona("The Board Member", "Investor", "Quarterly growth, churn reduction, exit strategy", "Critic"),

        # --- THE SPECIALISTS (The Deep Cuts) ---
        Persona("The Game Dev", "Unity/Unreal Engine Dev", "Frame rates, asset pipelines, C++ interop", "Maker"),
        Persona("The Embedded Engineer", "Firmware Dev", "Memory constraints, RTOS, hardware debugging", "Maker"),
        Persona("The Data Engineer", "Pipeline Architect", "ETL latency, data quality, Snowflake costs", "Maker"),
        Persona("The Penetration Tester", "White Hat Hacker", "SQL injection, XSS, privilege escalation", "Critic"),
        Persona("The SRE", "Site Reliability Engineer", "Uptime, error budgets, on-call fatigue", "Critic"),
        Persona("The ML Researcher", "PhD Candidate", "Novelty, paper citations, state-of-the-art", "Hype"),

        # --- THE REGIONAL USERS (Global Context) ---
        Persona("The EU User", "Privacy Advocate", "Cookies, GDPR, right to be forgotten, US servers", "Critic"),
        Persona("The China User", "Global Dev", "GFW latency, npm mirrors, localization support", "User"),
        Persona("The Emerging Market User", "Mobile User", "Low bandwidth, old Android device, offline support", "User"),
        Persona("The Silicon Valley Founder", "Tech Bro", "Networking, advisory board, YC combinator", "Hype"),
        Persona("The Tokyo Salaryman", "Enterprise User", "Formal emails, hierarchy, Excel macros", "User"),
        Persona("The Berlin Artist", "Creative Coder", "Processing, generative art, aesthetics", "Maker"),

        # --- THE NICHE (Edge Cases) ---
        Persona("The Accessibility Tester", "Blind User", "Screen reader compatibility, aria-labels", "Critic"),
        Persona("The Dark Web Researcher", "Anon", "Tor, privacy, crypto payments, no logs", "User"),
    ]

    RAP_PROMPT = """
    CONTEXT: {trends}
    
    TASK: Analyze the following feature idea for a {domain} product.
    FEATURE: "{feature}"
    
    YOUR ROLE:
    You are a simulated panel of users. 
    You DO NOT speak generically. You speak from your specific OBSESSIONS and the CURRENT MARKET CONTEXT (Hype).
    
    If the market context mentions "DeepSeek" or "Cursor", and you are a Dev, you mention it.
    If the context mentions "Security breaches", and you are Sec, you freak out.
    
    SELECTED PANEL:
    {panel_text}
    
    INSTRUCTIONS:
    - BE BRUTAL. No polite corporate speak.
    - BE SPECIFIC. Reference the "Current Hype" if relevant.
    - SHORT & PUNCHY. One or two sentences per persona.
    
    OUTPUT FORMAT:
    [Persona Name]: [Reaction]
    """

    def __init__(self, db: Optional[SimplifiedDatabase] = None, project_path: Optional[Path] = None, allow_fallbacks: bool = True):
        self.db = db
        self.project_path = project_path
        self.project_id = SimplifiedDatabase.get_project_id(project_path) if project_path else "unknown"
        self.strategist = Strategist(db, project_path, allow_fallbacks=allow_fallbacks)
        self.signals = SignalAggregator()
        self.allow_fallbacks = allow_fallbacks

    async def simulate_feedback(self, feature: str, domain: str = "General Software") -> str:
        """
        Run a simulation of the feature against Retrieval Augmented Personas (RAP).
        """
        # 1. RETRIEVAL: Fetch live market signals to ground the simulation
        # We fetch top 5 headlines to create the "Vibe Context"
        logger.info(f"Retrieving live signals for RAP context in domain: {domain}")
        live_signals = await self.signals.fetch_signals(domain)
        
        # Summarize hype into a context string
        hype_lines = []
        for s in live_signals[:5]:
            hype_lines.append(f"- {s['title']} ({s['source']})")
        
        hype_context = "current industry trends:\n" + ("\n".join(hype_lines) if hype_lines else "Standard market conditions.")

        # 2. SELECTION: Randomly select 5 personas (balanced mix) or hardcoded relevant ones?
        # For a "Strategic" view, let's pick 5 distinct ones to avoid token overflow, 
        # but ensure we get at least 1 Critic, 1 User, 1 Hype, 1 Maker.
        import random
        panel = []
        for cat in ["Critic", "User", "Hype", "Maker"]:
            candidates = [p for p in self.PERSONAS if p.category == cat]
            if candidates:
                panel.append(random.choice(candidates))
        # Add one random wildcard
        panel.append(random.choice(self.PERSONAS))

        panel_text = "\n".join([f"- {p.name} ({p.role}): Obsessed with {p.obsessions}" for p in panel])
        
        prompt = self.RAP_PROMPT.format(
            trends=hype_context,
            domain=domain,
            feature=feature,
            panel_text=panel_text
        )
        
        # 3. GENERATION: Run the simulation
        response = await self.strategist._call_groq(
            prompt,
            model=self.strategist.SMART_MODEL,
            max_tokens=800,
            temperature=0.8  # High temp for distinct voices
        )
        
        if not response:
            if not self.allow_fallbacks:
                raise RuntimeError("Simulation failed (Silent Panel) and fallbacks are disabled (STRICT_MODE)")
            response = "[SIMULATION FALLBACK] Panel is unavailable. Simulation based on heuristics: 'Looks scalable but check GDPR.'"

        if self.db:
            self.db.log_activity(
                project_id=self.project_id,
                tool="simulator",
                action="simulate_feedback",
                cost_tokens=100 if "FALLBACK" in response else 2000,
                tier="free",
                payload={"feature": feature[:100], "panel_size": len(panel), "fallback": "FALLBACK" in response}
            )

        return f"### 🔮 Live Persona Context\nBased on real-time signals:\n{hype_context}\n\n### 🗣️ Panel Feedback\n{response}"
