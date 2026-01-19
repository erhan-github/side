"""
Zero-Storage RAG - Retrieval-Augmented Generation using trending APIs.

Fetches trending signals on-demand, no database storage.
"""

from typing import Any
import logging

from side.intel.trending import get_trending_signals
from side.intel.strategist import Strategist

logger = logging.getLogger(__name__)


async def retrieve_trending_signals(
    query: str,
    category: str = None,
    limit: int = 5
) -> list[dict[str, Any]]:
    """
    Retrieve trending signals relevant to a query.
    
    Fetches from trending APIs on-demand.
    
    Args:
        query: User's question
        category: Optional category filter
        limit: Max signals to return
    
    Returns:
        List of relevant trending signals
    """
    # Fetch trending signals (no storage)
    all_signals = await get_trending_signals(max_results=20)
    
    # Filter by query keywords
    query_lower = query.lower()
    keywords = []
    
    # Extract tech terms from query
    tech_terms = [
        'redis', 'postgres', 'mongodb', 'supabase', 'firebase',
        'auth', 'authentication', 'stripe', 'payment',
        'react', 'vue', 'nextjs', 'typescript', 'python', 'rust',
        'llm', 'gpt', 'reasoning', 'benchmark', 'ai', 'ml'
    ]
    
    for term in tech_terms:
        if term in query_lower:
            keywords.append(term)
    
    # Filter signals by keywords
    relevant = []
    for signal in all_signals:
        text = f"{signal['title']} {signal.get('description', '')}".lower()
        
        # Check if any keyword matches
        if keywords:
            if any(kw in text for kw in keywords):
                relevant.append(signal)
        else:
            # No specific keywords, use category
            if category and signal.get('category') == category:
                relevant.append(signal)
            elif not category:
                relevant.append(signal)
    
    # Sort by score and return top N
    relevant.sort(key=lambda x: x.get('score', 0), reverse=True)
    return relevant[:limit]


def format_signals_for_context(signals: list[dict[str, Any]]) -> str:
    """
    Format signals as context for LLM.
    
    Args:
        signals: List of signal dicts
    
    Returns:
        Formatted context string
    """
    if not signals:
        return ""
    
    context = "## Trending Intelligence Signals\n\n"
    context += "Here are trending signals from GitHub, HackerNews, Dev.to, and ArXiv:\n\n"
    
    for i, signal in enumerate(signals, 1):
        context += f"{i}. **{signal['title']}**\n"
        if signal.get('description'):
            context += f"   - {signal['description'][:100]}...\n"
        context += f"   - Source: {signal['source']}\n"
        context += f"   - URL: {signal['url']}\n"
        
        # Add metadata
        if signal.get('metadata'):
            meta = signal['metadata']
            if meta.get('stars'):
                context += f"   - ⭐ {meta['stars']} stars\n"
            if meta.get('score'):
                context += f"   - 🔥 {meta['score']} points\n"
        
        context += "\n"
    
    return context


async def answer_with_trending(
    question: str,
    category: str = None,
    use_signals: bool = True
) -> dict[str, Any]:
    """
    Answer a question using RAG with trending signals.
    
    Zero-storage approach - fetches trending data on-demand.
    
    Args:
        question: User's question
        category: Optional category hint
        use_signals: Whether to use signals
    
    Returns:
        Dict with answer and metadata
    """
    # 1. Retrieve trending signals
    signals = []
    if use_signals:
        signals = await retrieve_trending_signals(question, category=category, limit=5)
        logger.info(f"Retrieved {len(signals)} trending signals")
    
    # 2. Format signals as context
    signal_context = format_signals_for_context(signals)
    
    # 3. Build enhanced prompt
    if signal_context:
        enhanced_prompt = f"""You are Side, a strategic AI assistant for developers.

{signal_context}

User Question: {question}

Based on the trending signals above and your knowledge, provide a helpful, actionable answer.
Focus on what's trending NOW and cite the signals when relevant.
"""
    else:
        enhanced_prompt = f"""You are Side, a strategic AI assistant for developers.

User Question: {question}

Provide a helpful, actionable answer based on your knowledge.
"""
    
    # 4. Get LLM answer
    strategist = Strategist()
    answer = await strategist.ask_llm(enhanced_prompt)
    
    return {
        'answer': answer,
        'signals_used': len(signals),
        'signal_titles': [s['title'] for s in signals],
        'enhanced': len(signals) > 0
    }


# Use case functions

async def find_trending_alternatives(tool_name: str) -> dict[str, Any]:
    """
    Find trending alternatives to a tool.
    
    Example: find_trending_alternatives("Redis")
    """
    question = f"What are trending alternatives to {tool_name}?"
    return await answer_with_trending(question, category='competition')


async def whats_trending_in(topic: str) -> dict[str, Any]:
    """
    What's trending in a topic.
    
    Example: whats_trending_in("LLM reasoning")
    """
    question = f"What's trending in {topic}? Any recent breakthroughs?"
    return await answer_with_trending(question, category='llm_research')


async def trending_repos(language: str = None) -> list[dict[str, Any]]:
    """
    Get trending GitHub repos.
    
    Example: trending_repos("python")
    """
    from side.intel.trending import get_trending_repos
    return await get_trending_repos(language=language)


if __name__ == "__main__":
    # Test the zero-storage RAG
    import asyncio
    
    async def test():
        print("\n" + "="*70)
        print("ZERO-STORAGE RAG TEST")
        print("="*70)
        
        # Test 1: Find trending alternatives
        print("\n1. Testing: What's trending in AI agents?")
        signals = await retrieve_trending_signals("AI agents", limit=3)
        print(f"   Found {len(signals)} trending signals:")
        for sig in signals:
            print(f"   - {sig['title'][:60]}...")
        
        print("\n✅ Zero-storage RAG working!")
        print("="*70 + "\n")
    
    asyncio.run(test())
