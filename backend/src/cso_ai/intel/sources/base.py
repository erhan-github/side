
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

# Domain Definitions
DomainType = Literal["tech", "market", "legal", "investment", "general"]

@dataclass
class IntelligenceItem:
    """Standardized intelligence item across all domains."""
    id: str
    title: str
    url: str
    source: str
    domain: DomainType = "tech"
    description: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    fetched_at: datetime = field(default_factory=datetime.utcnow)
    
    # Metadata for specific domains
    tags: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    
    # Scoring (filled by analyzer)
    relevance_score: float | None = None
    relevance_reason: str | None = None

class SourcePlugin(ABC):
    """Abstract base class for all intelligence source plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the source plugin."""
        pass
        
    @property
    @abstractmethod
    def domain(self) -> DomainType:
        """Primary domain of this source."""
        pass
    
    @abstractmethod
    async def fetch(self, limit: int = 10) -> list[IntelligenceItem]:
        """Fetch latest items from the source."""
        pass
        
    @abstractmethod
    async def close(self) -> None:
        """Clean up resources."""
        pass
