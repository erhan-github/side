"""
Sovereign Pricing Strategy - Single Source of Truth.
Aligned with Sidelith Business Model v1.1
"""
from enum import Enum

class Tier(str, Enum):
    HOBBY = "hobby"
    PRO = "pro"
    ELITE = "elite"
    HITECH = "hitech"

class PricingModel:
    # Monthly Sovereign Unit (SU) Limits
    LIMITS = {
        Tier.HOBBY: 500,
        Tier.PRO: 5000,
        Tier.ELITE: 25000,
        Tier.HITECH: 999999999 # effectively unlimited / custom
    }

    # Display Names
    LABELS = {
        Tier.HOBBY: "Hobby",
        Tier.PRO: "Pro",
        Tier.ELITE: "Elite",
        Tier.HITECH: "High Tech"
    }

    @classmethod
    def get_limit(cls, tier: str) -> int:
        return cls.LIMITS.get(Tier(tier), 500) # Default to Hobby

    @classmethod
    def detect_tier(cls, key: str) -> str:
        """
        [GENESIS LOGIC]: Determines Tier from the Sovereign Key prefix.
        Format: sk_[tier]_[hash]
        """
        if not key: return cls.LABELS[Tier.HOBBY]
        
        if "sk_elite" in key: return Tier.ELITE
        if "sk_pro" in key:   return Tier.PRO
        if "sk_hitech" in key: return Tier.HITECH
        
        if "sk_hitech" in key: return Tier.HITECH
        
        # Default for 'sk_hobby' or unknown/legacy keys
        return Tier.HOBBY

class ActionCost:
    """
    [SOFTWARE 2.0 ECONOMY]: The cost of Sovereign Actions in SUs.
    """
    SIGNAL_CAPTURE = 1     # Real-time terminal ingestion
    HUB_EVOLVE = 10        # Strategic Hub update (plan/check)
    FORENSIC_PULSE = 10    # Deep forensic analysis
    CONTEXT_BOOST = 15     # High-fidelity architectural audit
    IDENTITY_RECONFIG = 30 # Authentication logic change (Rotation/Migration)
    LOGIC_MUTATION = 50    # Architectural refactor
    STRATEGIC_ALIGN = 50   # Strategic goal drift detection
    WELCOME = 0            # Administrative Bootstrap (Free)

class LLMUsage:
    """
    [RAW COMPUTE]: The cost of Raw Intelligence (per 1k tokens).
    Sidelith charges for both 'Strategic Actions' (Value) and 'Raw Compute' (Cost).
    """
    # 1 SU = 1 cent roughly (Abstract)
    INPUT_1K = 0.5    # 0.5 SU per 1k input tokens (High quality context)
    OUTPUT_1K = 1.0   # 1.0 SU per 1k output tokens (Code generation)
    
    # Reasoning Models (o1/o3-mini/r1)
    REASONING_1K = 5.0 # 5.0 SUs per 1k reasoning tokens
