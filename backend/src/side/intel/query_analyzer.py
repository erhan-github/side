"""
Query Analyzer - Detects intent and selects optimal filters.

Analyzes user queries to determine:
- Intent: trending, best, latest, search
- Domain: code, research, tutorials, general
- Keywords: extracted tech terms
- Time window: today, week, month
"""

import re
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class QueryIntent(str, Enum):
    """Query intent types."""
    TRENDING = "trending"
    BEST = "best"
    LATEST = "latest"
    SEARCH = "search"
    COMPARISON = "comparison"


class QueryDomain(str, Enum):
    """Query domain types."""
    CODE = "code"
    RESEARCH = "research"
    TUTORIALS = "tutorials"
    GENERAL = "general"


@dataclass
class QueryContext:
    """Analyzed query context."""
    query: str
    intent: QueryIntent
    domain: QueryDomain
    keywords: List[str]
    time_window: str  # "day", "week", "month"
    language: Optional[str] = None  # Programming language if detected


class QueryAnalyzer:
    """Analyzes queries to determine intent and context."""
    
    # Intent detection patterns
    INTENT_PATTERNS = {
        QueryIntent.TRENDING: [
            r'\b(trending|hot|popular|viral|buzz)\b',
            r'\bwhat\'?s (hot|trending|popular)\b',
        ],
        QueryIntent.BEST: [
            r'\b(best|top|recommended|favorite)\b',
            r'\bwhat\'?s the best\b',
        ],
        QueryIntent.LATEST: [
            r'\b(latest|new|recent|newest|just released)\b',
            r'\bwhat\'?s new\b',
        ],
        QueryIntent.COMPARISON: [
            r'\b(vs|versus|alternative|instead of|replace)\b',
            r'\bcompare\b',
        ],
    }
    
    # Domain detection patterns
    DOMAIN_PATTERNS = {
        QueryDomain.CODE: [
            r'\b(library|framework|tool|package|repo|github)\b',
            r'\b(code|programming|developer|api)\b',
        ],
        QueryDomain.RESEARCH: [
            r'\b(paper|research|study|arxiv|benchmark)\b',
            r'\b(llm|ai|ml|machine learning)\b',
        ],
        QueryDomain.TUTORIALS: [
            r'\b(tutorial|guide|how to|learn|course)\b',
            r'\b(beginner|getting started)\b',
        ],
    }
    
    # Programming languages
    LANGUAGES = [
        'python', 'javascript', 'typescript', 'rust', 'go', 'java',
        'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'scala'
    ]
    
    # Tech keywords
    TECH_KEYWORDS = [
        'redis', 'postgres', 'mongodb', 'mysql', 'sqlite',
        'react', 'vue', 'angular', 'svelte', 'nextjs',
        'auth', 'authentication', 'payment', 'stripe',
        'docker', 'kubernetes', 'aws', 'gcp', 'azure',
        'llm', 'gpt', 'ai', 'ml', 'reasoning', 'benchmark'
    ]
    
    def analyze(self, query: str) -> QueryContext:
        """
        Analyze a query and return context.
        
        Args:
            query: User's query string
        
        Returns:
            QueryContext with detected intent, domain, keywords, etc.
        """
        query_lower = query.lower()
        
        # Detect intent
        intent = self._detect_intent(query_lower)
        
        # Detect domain
        domain = self._detect_domain(query_lower)
        
        # Extract keywords
        keywords = self._extract_keywords(query_lower)
        
        # Detect time window
        time_window = self._detect_time_window(query_lower)
        
        # Detect programming language
        language = self._detect_language(query_lower)
        
        return QueryContext(
            query=query,
            intent=intent,
            domain=domain,
            keywords=keywords,
            time_window=time_window,
            language=language
        )
    
    def _detect_intent(self, query: str) -> QueryIntent:
        """Detect query intent."""
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent
        
        # Default to search
        return QueryIntent.SEARCH
    
    def _detect_domain(self, query: str) -> QueryDomain:
        """Detect query domain."""
        for domain, patterns in self.DOMAIN_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return domain
        
        # Default to general
        return QueryDomain.GENERAL
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract tech keywords from query."""
        keywords = []
        
        for keyword in self.TECH_KEYWORDS:
            if keyword in query:
                keywords.append(keyword)
        
        return keywords
    
    def _detect_time_window(self, query: str) -> str:
        """Detect time window from query."""
        if re.search(r'\b(today|now)\b', query):
            return "day"
        elif re.search(r'\b(this week|weekly)\b', query):
            return "week"
        elif re.search(r'\b(this month|monthly)\b', query):
            return "month"
        
        # Default to week
        return "week"
    
    def _detect_language(self, query: str) -> Optional[str]:
        """Detect programming language from query."""
        for lang in self.LANGUAGES:
            if lang in query:
                return lang
        
        return None


# Convenience functions

def analyze_query(query: str) -> QueryContext:
    """Quick query analysis."""
    analyzer = QueryAnalyzer()
    return analyzer.analyze(query)


def get_intent(query: str) -> QueryIntent:
    """Get just the intent."""
    return analyze_query(query).intent


def get_keywords(query: str) -> List[str]:
    """Get just the keywords."""
    return analyze_query(query).keywords


if __name__ == "__main__":
    # Test the analyzer
    test_queries = [
        "What's trending in Python?",
        "Best Redis alternatives",
        "Latest AI research papers",
        "How to learn Rust",
        "React vs Vue comparison",
        "New authentication libraries",
    ]
    
    analyzer = QueryAnalyzer()
    
    print("\n" + "="*70)
    print("QUERY ANALYZER TEST")
    print("="*70 + "\n")
    
    for query in test_queries:
        context = analyzer.analyze(query)
        print(f"Query: \"{query}\"")
        print(f"  Intent: {context.intent}")
        print(f"  Domain: {context.domain}")
        print(f"  Keywords: {context.keywords}")
        print(f"  Time: {context.time_window}")
        if context.language:
            print(f"  Language: {context.language}")
        print()
    
    print("="*70)
    print("✅ Query analyzer working!")
    print("="*70 + "\n")
