"""
Side Text Analysis Pipeline - Pre-LLM Strategic Filtering.

Filters 200 articles down to 20 using cheap keyword matching,
then LLM scores only the strategic 20.

Cost: $0.00 (text analysis) + $0.001 (LLM on 20 articles) = $0.001/day
"""

import re
from collections import Counter
from typing import Any


# Strategic keywords by use case
STRATEGIC_KEYWORDS = {
    'competition': [
        'alternative', 'vs', 'comparison', 'competitor', 'better than',
        'instead of', 'replace', 'migration', 'switch from'
    ],
    'open_source': [
        'github', 'open source', 'oss', 'mit license', 'apache',
        'fork', 'stars', 'self-hosted', 'open-source'
    ],
    'llm_research': [
        'reasoning', 'benchmark', 'gpt', 'llama', 'chain-of-thought',
        'sota', 'state-of-the-art', 'prompt', 'agent', 'planning',
        'tool use', 'function calling', 'rag', 'retrieval'
    ],
    'framework': [
        'framework', 'library', 'released', 'v1.0', 'stable',
        'production-ready', 'typescript', 'react', 'next.js'
    ],
    'performance': [
        'faster', 'performance', 'optimization', 'benchmark',
        'latency', 'throughput', 'scalability', '10x', '5x'
    ]
}


def extract_keywords(text: str, top_n: int = 5) -> list[str]:
    """
    Extract top keywords from text using frequency analysis.
    
    Args:
        text: Input text (title + description)
        top_n: Number of keywords to return
    
    Returns:
        List of top keywords
    """
    # Common words to ignore
    stop_words = {
        'the', 'a', 'an', 'in', 'on', 'at', 'for', 'to', 'of', 'and',
        'is', 'it', 'this', 'that', 'with', 'from', 'by', 'are', 'was',
        'be', 'been', 'have', 'has', 'had', 'will', 'would', 'can', 'could',
        'should', 'may', 'might', 'must', 'shall', 'do', 'does', 'did',
        'but', 'or', 'as', 'if', 'when', 'where', 'which', 'who', 'what',
        'how', 'why', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
        'so', 'than', 'too', 'very', 'just', 'about', 'into', 'through',
        'during', 'before', 'after', 'above', 'below', 'between', 'under'
    }
    
    # Extract words (4+ chars)
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    
    # Filter out stop words
    filtered = [w for w in words if w not in stop_words]
    
    # Get top N most common
    return [word for word, _ in Counter(filtered).most_common(top_n)]


def detect_category(title: str, description: str = "") -> str | None:
    """
    Categorize article based on strategic keywords.
    
    Args:
        title: Article title
        description: Article description/abstract
    
    Returns:
        Category name or None if not strategic
    """
    text = f"{title} {description}".lower()
    
    # Check each category
    for category, keywords in STRATEGIC_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    
    return None


def extract_one_liner(title: str, description: str = "") -> str:
    """
    Extract a concise one-line summary.
    
    Args:
        title: Article title
        description: Article description
    
    Returns:
        One-line summary (max 150 chars)
    """
    # If title is descriptive enough, use it
    if 30 <= len(title) <= 100:
        return title
    
    # Otherwise, use first sentence of description
    if description:
        # Get first sentence
        first_sentence = description.split('.')[0].strip()
        if len(first_sentence) > 20:
            return first_sentence[:150]
    
    # Fallback to title
    return title[:150]


def filter_strategic_articles(
    articles: list[dict[str, Any]],
    max_results: int = 20
) -> list[dict[str, Any]]:
    """
    Filter articles to only strategic ones using keyword matching.
    
    This is the PRE-LLM filter that reduces 200 articles to 20.
    
    Args:
        articles: List of article dicts with 'title' and 'description'
        max_results: Max articles to return
    
    Returns:
        Filtered list of strategic articles with added metadata
    """
    strategic = []
    
    for article in articles:
        title = article.get('title', '')
        description = article.get('description', '')
        
        # Detect category
        category = detect_category(title, description)
        
        if category:
            # Extract keywords
            keywords = extract_keywords(f"{title} {description}")
            
            # Extract one-liner
            one_liner = extract_one_liner(title, description)
            
            # Add metadata
            article['category'] = category
            article['keywords'] = keywords
            article['one_liner'] = one_liner
            
            strategic.append(article)
            
            # Stop if we have enough
            if len(strategic) >= max_results:
                break
    
    return strategic


def score_article_heuristic(article: dict[str, Any]) -> int:
    """
    Simple heuristic scoring (0-100) without LLM.
    
    Used for initial sorting before LLM scoring.
    
    Args:
        article: Article dict with metadata
    
    Returns:
        Heuristic score (0-100)
    """
    score = 50  # Base score
    
    title = article.get('title', '').lower()
    description = article.get('description', '').lower()
    category = article.get('category', '')
    
    # Boost for high-value categories
    if category == 'llm_research':
        score += 20
    elif category == 'competition':
        score += 15
    elif category == 'open_source':
        score += 10
    
    # Boost for GitHub links
    if 'github.com' in article.get('url', ''):
        score += 10
    
    # Boost for ArXiv papers
    if 'arxiv.org' in article.get('url', ''):
        score += 15
    
    # Boost for specific high-value terms
    high_value_terms = ['benchmark', 'sota', 'state-of-the-art', 'breakthrough']
    if any(term in title or term in description for term in high_value_terms):
        score += 10
    
    # Penalty for low-quality signals
    low_quality_terms = ['tutorial', 'beginner', 'introduction', 'getting started']
    if any(term in title for term in low_quality_terms):
        score -= 10
    
    return max(0, min(100, score))
