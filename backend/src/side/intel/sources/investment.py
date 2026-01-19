
from datetime import datetime
from typing import Any

import httpx

from side.intel.sources.base import DomainType, IntelligenceItem, SourcePlugin


class InvestmentHubPlugin(SourcePlugin):
    """Fetches investment and grant opportunities."""
    
    # Curated High-Signal Opportunities
    # In V2, this could be a dynamic external JSON manifest
    OPPORTUNITIES = [
        {
            "id": "yc_apply",
            "title": "Y Combinator Application Cycle",
            "url": "https://www.ycombinator.com/apply",
            "description": "Apply to YC. The standard deal is $500k.",
            "tags": ["accelerator", "general"],
            "domain_filter": None, # Relevant to all
        },
        {
            "id": "gd_grants",
            "title": "Google for Startups Founders Funds",
            "url": "https://www.campus.co/founders-funds/",
            "description": "Equity-free cash awards and hands-on support for Black and Latino founders.",
            "tags": ["grant", "equity-free"],
            "domain_filter": None,
        },
        {
            "id": "ethereum_esp",
            "title": "Ethereum Ecosystem Support Program",
            "url": "https://esp.ethereum.foundation/",
            "description": "Grants and support for the Ethereum ecosystem.",
            "tags": ["grant", "web3", "crypto"],
            "domain_filter": ["web3", "crypto", "blockchain", "defi"],
        },
        {
            "id": "polkadot_grants",
            "title": "Web3 Foundation Grants (Polkadot)",
            "url": "https://web3.foundation/grants/",
            "description": "Funding for software development and research in the Polkadot ecosystem.",
            "tags": ["grant", "web3"],
            "domain_filter": ["web3", "polkadot", "substrate"],
        },
        {
            "id": "oss_fund",
            "title": "GitHub Sponsors Fund",
            "url": "https://github.com/sponsors",
            "description": "Get funded for your open source work.",
            "tags": ["sponsorship", "oss"],
            "domain_filter": ["open source", "oss", "library", "framework"],
        },
    ]

    @property
    def name(self) -> str:
        return "Investment & Grants Hub"
        
    @property
    def domain(self) -> DomainType:
        return "investment"
    
    def set_context(self, domain: str | None = None) -> None:
        """Set the project domain context for filtering."""
        self._project_domain = domain.lower() if domain else None

    async def fetch(self, limit: int = 5) -> list[IntelligenceItem]:
        """Fetch opportunities filtered by project domain."""
        # For V1 of this plugin, we use the static curated list.
        # Future: Fetch from live API/RSS
        
        items = []
        project_domain = getattr(self, "_project_domain", "")
        
        for opp in self.OPPORTUNITIES:
            # Domain Filter Logic
            allowed_domains = opp.get("domain_filter")
            
            # If item has domain restrictions
            if allowed_domains:
                # If we don't know the project domain, skip specialized items OR show generic ones
                if not project_domain:
                    continue
                    
                # Check for match partial (simple keyword match)
                if not any(d in project_domain for d in allowed_domains):
                    continue
            
            items.append(IntelligenceItem(
                id=opp["id"],
                title=opp["title"],
                url=opp["url"],
                source="Investment Hub",
                domain="investment",
                description=opp["description"],
                published_at=datetime.utcnow(), # Evergreen
                tags=opp["tags"],
                meta={"type": "opportunity"}
            ))
            
        return items[:limit]

    async def close(self) -> None:
        pass
