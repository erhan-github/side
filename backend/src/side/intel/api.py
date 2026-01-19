"""
Unified Intelligence API - The main interface for Side's intelligence system.

Combines:
- Query analysis (intent detection)
- Smart filter selection
- Multi-source fetching (trending APIs + RSS feeds)
- Zero-storage approach
- Error resilience

Usage:
    intelligence = IntelligenceAPI()
    result = await intelligence.answer("What's trending in Python?")
"""

import asyncio
from typing import Any, Dict, List
import logging

from side.intel.query_analyzer import QueryAnalyzer, QueryIntent, QueryDomain
from side.intel.trending import get_trending_signals
from side.intel.rss_fetcher import ResilientRSSFetcher, get_fresh_content
from side.intel.text_analysis import filter_strategic_articles
from side.intel.strategist import Strategist

logger = logging.getLogger(__name__)


class IntelligenceAPI:
    """
    Main intelligence API - analyzes queries and fetches relevant signals.
    
    Zero-storage, error-resilient, always fresh.
    """
    
    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
        self.rss_fetcher = ResilientRSSFetcher()
        self.strategist = Strategist()
    
    async def get_signals(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get relevant signals for a query.
        
        Args:
            query: User's query
            max_results: Max signals to return
        
        Returns:
            List of relevant signals
        """
        # 1. Analyze query
        context = self.query_analyzer.analyze(query)
        logger.info(f"Query intent: {context.intent}, domain: {context.domain}")
        
        # 2. Fetch from appropriate sources based on intent
        if context.intent == QueryIntent.TRENDING:
            # Use trending APIs
            signals = await self._fetch_trending(context)
        
        elif context.intent == QueryIntent.LATEST:
            # Use recent/new filters
            signals = await self._fetch_latest(context)
        
        elif context.intent == QueryIntent.BEST:
            # Use top/best filters
            signals = await self._fetch_best(context)
        
        else:  # SEARCH or COMPARISON
            # Use search + RSS feeds
            signals = await self._fetch_search(context)
        
        # 3. Filter to strategic signals
        strategic = filter_strategic_articles(signals, max_results=max_results * 2)
        
        # 4. Sort by relevance and return top N
        from side.intel.text_analysis import score_article_heuristic
        for signal in strategic:
            if 'score' not in signal:
                signal['score'] = score_article_heuristic(signal)
        
        strategic.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return strategic[:max_results]
    
    async def _fetch_trending(self, context) -> List[Dict[str, Any]]:
        """Fetch trending signals."""
        # Use trending APIs (GitHub, HN, Dev.to, ArXiv)
        return await get_trending_signals(
            github_since=context.time_window if context.time_window != "day" else "daily",
            max_results=20
        )
    
    async def _fetch_latest(self, context) -> List[Dict[str, Any]]:
        """Fetch latest signals."""
        if context.domain == QueryDomain.RESEARCH:
            # ArXiv recent papers
            from side.intel.trending import fetch_arxiv_recent
            return await fetch_arxiv_recent(days=7)
        else:
            # RSS feeds (latest articles)
            return await get_fresh_content(max_articles=50)
    
    async def _fetch_best(self, context) -> List[Dict[str, Any]]:
        """Fetch best/top signals."""
        # Combine trending (which are "best" by definition) + RSS
        trending = await get_trending_signals(max_results=10)
        rss = await get_fresh_content(max_articles=20)
        return trending + rss
    
    async def _fetch_search(self, context) -> List[Dict[str, Any]]:
        """Fetch search results."""
        # For now, use RSS feeds + trending
        # TODO: Add search-specific APIs
        trending = await get_trending_signals(max_results=10)
        rss = await get_fresh_content(max_articles=30)
        return trending + rss
    
    async def answer(
        self,
        question: str,
        use_signals: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a question using intelligence signals.
        
        Args:
            question: User's question
            use_signals: Whether to use signals (for A/B testing)
        
        Returns:
            Dict with answer and metadata
        """
        # 1. Get relevant signals
        signals = []
        if use_signals:
            signals = await self.get_signals(question, max_results=5)
            logger.info(f"Retrieved {len(signals)} signals")
        
        # 2. Format signals as context
        signal_context = self._format_signals(signals)
        
        # 3. Build prompt
        if signal_context:
            prompt = f"""You are Side, a strategic AI assistant for developers.

{signal_context}

User Question: {question}

Based on the signals above and your knowledge, provide a helpful, actionable answer.
Focus on what's trending/latest and cite the signals when relevant.
"""
        else:
            prompt = f"""You are Side, a strategic AI assistant for developers.

User Question: {question}

Provide a helpful, actionable answer based on your knowledge.
"""
        
        # 4. Get LLM answer
        answer = await self.strategist.ask_llm(prompt)
        
        return {
            'answer': answer,
            'signals_used': len(signals),
            'signal_titles': [s['title'] for s in signals],
            'enhanced': len(signals) > 0
        }
    
    def _format_signals(self, signals: List[Dict[str, Any]]) -> str:
        """Format signals as context for LLM."""
        if not signals:
            return ""
        
        context = "## Intelligence Signals\n\n"
        
        for i, signal in enumerate(signals, 1):
            context += f"{i}. **{signal['title']}**\n"
            if signal.get('description'):
                context += f"   {signal['description'][:150]}...\n"
            context += f"   Source: {signal['source']} | URL: {signal['url']}\n"
            context += "\n"
        
        return context


# Convenience functions

async def ask_side(question: str) -> str:
    """
    Quick way to ask Side a question.
    
    Args:
        question: User's question
    
    Returns:
        Answer string
    """
    api = IntelligenceAPI()
    result = await api.answer(question)
    return result['answer']


async def get_trending(topic: str = None) -> List[Dict[str, Any]]:
    """
    Get trending signals.
    
    Args:
        topic: Optional topic filter
    
    Returns:
        List of trending signals
    """
    api = IntelligenceAPI()
    query = f"What's trending in {topic}?" if topic else "What's trending?"
    return await api.get_signals(query)


if __name__ == "__main__":
    # Test the unified API
    async def test():
        print("\n" + "="*70)
        print("UNIFIED INTELLIGENCE API TEST")
        print("="*70)
        
        api = IntelligenceAPI()
        
        # Test 1: Get trending signals
        print("\n1. Testing: What's trending in Python?")
        signals = await api.get_signals("What's trending in Python?", max_results=5)
        print(f"   Found {len(signals)} signals:")
        for i, sig in enumerate(signals, 1):
            print(f"   {i}. {sig['title'][:55]}... ({sig['source']})")
        
        print("\n✅ Unified API working!")
        print("="*70 + "\n")
    
    asyncio.run(test())
