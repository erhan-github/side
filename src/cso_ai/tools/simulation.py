"""
Simulation tool handler for CSO.ai.

Handles: simulate

Implements Killer Features UX Strategy for virtual user simulation.
"""

import logging
from datetime import datetime, timezone
from typing import Any
import re

from cso_ai.tools.core import get_auto_intel, get_database
from cso_ai.tools.formatting import format_simulation
from cso_ai.utils import handle_tool_errors

logger = logging.getLogger(__name__)


@handle_tool_errors
async def handle_simulate(arguments: dict[str, Any]) -> str:
    """
    Simulate user feedback using Virtual Personas.
    
    Target: < 3 seconds
    """
    start_time = datetime.now(timezone.utc)
    feature = arguments.get("feature", "")
    
    if not feature:
        return "❌ Please specify a feature to simulate (e.g., 'simulate \"add dark mode\"')"
    
    # Auto-detect domain
    auto_intel = get_auto_intel()
    profile = await auto_intel.get_or_create_profile()
    domain = profile.domain or profile.to_dict().get("business", {}).get("domain", "General Software")
    
    # Run Simulation
    from cso_ai.intel.simulator import Simulator
    sim = Simulator()
    
    feedback = await sim.simulate_feedback(feature, domain)
    
    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    # Parse feedback to extract persona details
    # Default values if parsing fails
    persona_name = "TINA THE TEACHER"
    persona_quote = "I need this to be simpler."
    satisfaction = 5.0
    pain_points = ["Feature seems unclear", "Need better onboarding"]
    would_pay = "$15/mo (uncertain)"
    
    # Try to extract structured data from LLM response
    if feedback:
        lines = feedback.split("\n")
        
        # Look for persona name
        for line in lines:
            if "persona:" in line.lower() or "user:" in line.lower():
                persona_name = line.split(":")[-1].strip().upper()
                break
        
        # Look for satisfaction/rating
        rating_match = re.search(r'(\d+\.?\d*)\s*/\s*10', feedback)
        if rating_match:
            satisfaction = float(rating_match.group(1))
        
        # Extract pain points (lines starting with - or *)
        extracted_pains = []
        for line in lines:
            line = line.strip()
            if line.startswith(("-", "*", "•")):
                pain = line.lstrip("-*• ").strip()
                if len(pain) > 5 and len(pain) < 80:
                    extracted_pains.append(pain[:60])
        if extracted_pains:
            pain_points = extracted_pains[:3]
        
        # Look for quote
        quote_match = re.search(r'"([^"]{10,100})"', feedback)
        if quote_match:
            persona_quote = quote_match.group(1)
        
        # Look for price/willingness
        price_match = re.search(r'\$\d+', feedback)
        if price_match:
            would_pay = f"{price_match.group(0)}/mo"
    
    # Determine persona based on domain
    domain_personas = {
        "EdTech": "TINA THE TEACHER",
        "FinTech": "FRANK THE FINANCE BRO",
        "Healthcare": "HANNAH THE HOSPITAL ADMIN",
        "E-commerce": "EMMA THE ENTREPRENEUR",
        "SaaS": "SAM THE STARTUP FOUNDER",
    }
    for key, name in domain_personas.items():
        if key.lower() in domain.lower():
            persona_name = name
            break
    
    # Format with killer features style
    output = format_simulation(
        persona_name=persona_name,
        persona_quote=persona_quote,
        satisfaction=satisfaction,
        pain_points=pain_points,
        would_pay=would_pay,
        follow_up="Want me to redesign this flow?"
    )
    
    # Save simulation result as a learning
    try:
        db = get_database()
        db.save_learning(
            title=f"Simulation: {feature}",
            content=feedback,
            category="Simulation",
            tags=["simulation", domain.lower().replace(" ", "_")]
        )
    except Exception as e:
        logger.debug(f"Failed to save simulation learning: {e}")

    return output
