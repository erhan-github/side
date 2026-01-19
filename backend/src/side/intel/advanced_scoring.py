"""
Advanced Signal Scoring - Forensic-level intelligence quality.

Improvements:
1. Personalized scoring (tech stack matching)
2. Expert authority weighting
3. Time-based quality decay
4. Cross-reference detection
5. Signal clustering
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import re


# ═══════════════════════════════════════════════════════════════════
# EXPERT AUTHORITY SCORES
# ═══════════════════════════════════════════════════════════════════

EXPERT_AUTHORITY = {
    # Systems & Infrastructure
    "Julia Evans": {"networking": 0.95, "debugging": 0.90, "linux": 0.85},
    "Charity Majors": {"observability": 0.95, "devops": 0.90, "databases": 0.85},
    "Dan Luu": {"performance": 0.95, "hardware": 0.90, "optimization": 0.85},
    "Martin Kleppmann": {"distributed": 0.95, "databases": 0.90, "consistency": 0.85},
    "Brendan Gregg": {"performance": 0.95, "profiling": 0.90, "linux": 0.85},
    
    # Frontend
    "Dan Abramov": {"react": 0.95, "javascript": 0.90, "frontend": 0.85},
    "Kent C. Dodds": {"testing": 0.95, "react": 0.90, "javascript": 0.85},
    
    # Backend
    "Martin Fowler": {"architecture": 0.95, "patterns": 0.90, "refactoring": 0.85},
    
    # Security
    "Troy Hunt": {"security": 0.95, "web": 0.90, "authentication": 0.85},
    "Bruce Schneier": {"security": 0.95, "cryptography": 0.90, "privacy": 0.85},
    
    # AI/ML
    "Andrej Karpathy": {"ai": 0.95, "llm": 0.90, "deep-learning": 0.85},
    "Chip Huyen": {"mlops": 0.95, "ai": 0.90, "production": 0.85},
}


# ═══════════════════════════════════════════════════════════════════
# TECH STACK DETECTION
# ═══════════════════════════════════════════════════════════════════

def detect_tech_stack_from_signal(signal: Dict[str, Any]) -> List[str]:
    """
    Detect tech stack mentioned in a signal.
    
    Returns list of technologies: ['redis', 'postgres', 'react', etc.]
    """
    text = f"{signal.get('title', '')} {signal.get('description', '')}".lower()
    
    tech_keywords = {
        # Databases
        'redis', 'postgres', 'postgresql', 'mongodb', 'mysql', 'sqlite',
        'dragonfly', 'keydb', 'supabase', 'planetscale', 'neon',
        
        # Frontend
        'react', 'vue', 'angular', 'svelte', 'nextjs', 'remix', 'astro',
        
        # Backend
        'fastapi', 'django', 'flask', 'express', 'nestjs',
        
        # Languages
        'python', 'javascript', 'typescript', 'rust', 'go', 'java',
        
        # Infrastructure
        'docker', 'kubernetes', 'aws', 'gcp', 'azure', 'vercel', 'railway',
        
        # AI/ML
        'llm', 'gpt', 'openai', 'anthropic', 'langchain', 'huggingface',
        
        # Tools
        'github', 'gitlab', 'cursor', 'vscode',
    }
    
    detected = []
    for tech in tech_keywords:
        if tech in text:
            detected.append(tech)
    
    return detected


# ═══════════════════════════════════════════════════════════════════
# PERSONALIZED SCORING
# ═══════════════════════════════════════════════════════════════════

def calculate_personalized_score(
    signal: Dict[str, Any],
    user_stack: Optional[Dict[str, List[str]]] = None
) -> int:
    """
    Calculate personalized score based on user's tech stack.
    
    Args:
        signal: Signal dict
        user_stack: User's tech stack
            {
                'languages': ['python', 'typescript'],
                'frameworks': ['nextjs', 'fastapi'],
                'databases': ['postgres', 'redis'],
                'tools': ['docker', 'github']
            }
    
    Returns:
        Personalized score boost (0-30)
    """
    if not user_stack:
        return 0
    
    # Detect tech in signal
    signal_tech = detect_tech_stack_from_signal(signal)
    
    # Calculate overlap with user's stack
    boost = 0
    
    for category, user_techs in user_stack.items():
        for tech in user_techs:
            if tech in signal_tech:
                # Boost based on category importance
                if category == 'languages':
                    boost += 10  # High importance
                elif category == 'frameworks':
                    boost += 8
                elif category == 'databases':
                    boost += 6
                else:
                    boost += 4
    
    return min(boost, 30)  # Cap at 30


# ═══════════════════════════════════════════════════════════════════
# EXPERT AUTHORITY WEIGHTING
# ═══════════════════════════════════════════════════════════════════

def calculate_expert_boost(signal: Dict[str, Any]) -> int:
    """
    Boost score if signal is from recognized expert in relevant domain.
    
    Returns:
        Expert boost (0-20)
    """
    source = signal.get('source', '')
    
    if source not in EXPERT_AUTHORITY:
        return 0
    
    # Get expert's domains
    expert_domains = EXPERT_AUTHORITY[source]
    
    # Detect signal's domain from keywords
    signal_text = f"{signal.get('title', '')} {signal.get('description', '')}".lower()
    
    max_boost = 0
    for domain, authority in expert_domains.items():
        if domain in signal_text:
            # Boost based on authority score
            boost = int(authority * 20)  # 0.95 → 19 points
            max_boost = max(max_boost, boost)
    
    return max_boost


# ═══════════════════════════════════════════════════════════════════
# TIME-BASED QUALITY DECAY
# ═══════════════════════════════════════════════════════════════════

def calculate_freshness_score(signal: Dict[str, Any]) -> int:
    """
    Calculate freshness score with decay over time.
    
    Decay formula:
    - Day 1-3: No decay (100%)
    - Day 4-7: 5% decay per day
    - Day 8-14: 10% decay per day
    - Day 15+: 15% decay per day
    
    Returns:
        Freshness penalty (0 to -30)
    """
    published_at = signal.get('published_at')
    if not published_at:
        return -10  # Unknown age penalty
    
    try:
        if isinstance(published_at, str):
            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        else:
            pub_date = published_at
        
        days_old = (datetime.now(timezone.utc) - pub_date).days
        
        if days_old <= 3:
            return 0  # Fresh, no penalty
        elif days_old <= 7:
            return -(days_old - 3) * 2  # -2 per day
        elif days_old <= 14:
            return -8 - (days_old - 7) * 3  # -3 per day
        else:
            return -29  # Max penalty
    
    except Exception:
        return -10


# ═══════════════════════════════════════════════════════════════════
# CROSS-REFERENCE DETECTION
# ═══════════════════════════════════════════════════════════════════

def detect_cross_references(signals: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Detect signals that reference the same topic.
    
    Returns:
        Dict mapping signal_id to list of related signal_ids
    """
    cross_refs = defaultdict(list)
    
    # Extract key terms from each signal
    signal_terms = {}
    for signal in signals:
        text = f"{signal.get('title', '')} {signal.get('description', '')}".lower()
        
        # Extract significant terms (4+ chars, not common words)
        terms = set(re.findall(r'\b[a-z]{4,}\b', text))
        
        # Remove common words
        common = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 'they'}
        terms -= common
        
        signal_terms[signal['id']] = terms
    
    # Find overlapping terms
    for sig1_id, terms1 in signal_terms.items():
        for sig2_id, terms2 in signal_terms.items():
            if sig1_id == sig2_id:
                continue
            
            # Calculate overlap
            overlap = terms1 & terms2
            overlap_ratio = len(overlap) / max(len(terms1), len(terms2))
            
            # If >30% overlap, they're related
            if overlap_ratio > 0.3:
                cross_refs[sig1_id].append(sig2_id)
    
    return dict(cross_refs)


# ═══════════════════════════════════════════════════════════════════
# SIGNAL CLUSTERING
# ═══════════════════════════════════════════════════════════════════

def cluster_signals(signals: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Cluster similar signals by topic.
    
    Returns:
        Dict mapping topic to list of signals
    """
    clusters = defaultdict(list)
    
    for signal in signals:
        # Detect primary topic
        tech = detect_tech_stack_from_signal(signal)
        
        if tech:
            # Use first detected tech as cluster key
            cluster_key = tech[0]
        else:
            # Use category as fallback
            cluster_key = signal.get('category', 'general')
        
        clusters[cluster_key].append(signal)
    
    return dict(clusters)


# ═══════════════════════════════════════════════════════════════════
# ADVANCED SCORING PIPELINE
# ═══════════════════════════════════════════════════════════════════

def calculate_advanced_score(
    signal: Dict[str, Any],
    user_stack: Optional[Dict[str, List[str]]] = None,
    base_score: int = 50
) -> int:
    """
    Calculate advanced score with all quality improvements.
    
    Scoring components:
    - Base heuristic score: 0-100
    - Personalization boost: 0-30
    - Expert authority boost: 0-20
    - Freshness penalty: 0 to -30
    
    Final score: 0-150 (capped at 100 for display)
    
    Args:
        signal: Signal dict
        user_stack: User's tech stack (optional)
        base_score: Base heuristic score
    
    Returns:
        Final score (0-100)
    """
    score = base_score
    
    # 1. Personalization boost
    personalization = calculate_personalized_score(signal, user_stack)
    score += personalization
    
    # 2. Expert authority boost
    expert_boost = calculate_expert_boost(signal)
    score += expert_boost
    
    # 3. Freshness penalty
    freshness = calculate_freshness_score(signal)
    score += freshness
    
    # 4. Source quality boost
    source = signal.get('source', '')
    if source == 'arxiv':
        score += 10  # Academic papers are high quality
    elif source == 'github':
        # Boost based on stars
        stars = signal.get('metadata', {}).get('stars', 0)
        if stars > 10000:
            score += 15
        elif stars > 5000:
            score += 10
        elif stars > 1000:
            score += 5
    elif source == 'hackernews':
        # Boost based on HN score
        hn_score = signal.get('metadata', {}).get('score', 0)
        if hn_score > 500:
            score += 15
        elif hn_score > 200:
            score += 10
        elif hn_score > 100:
            score += 5
    
    # Cap at 100 for display
    return min(max(score, 0), 100)


# ═══════════════════════════════════════════════════════════════════
# SIGNAL ENRICHMENT
# ═══════════════════════════════════════════════════════════════════

def enrich_signal(
    signal: Dict[str, Any],
    user_stack: Optional[Dict[str, List[str]]] = None
) -> Dict[str, Any]:
    """
    Enrich signal with quality metadata.
    
    Adds:
    - Advanced score
    - Detected tech stack
    - Expert authority flag
    - Freshness indicator
    - Cross-reference count
    """
    # Calculate advanced score
    base_score = signal.get('score', 50)
    signal['advanced_score'] = calculate_advanced_score(signal, user_stack, base_score)
    
    # Detect tech stack
    signal['detected_tech'] = detect_tech_stack_from_signal(signal)
    
    # Check if from expert
    signal['is_expert'] = signal.get('source', '') in EXPERT_AUTHORITY
    
    # Calculate freshness
    freshness = calculate_freshness_score(signal)
    if freshness == 0:
        signal['freshness'] = 'fresh'
    elif freshness > -10:
        signal['freshness'] = 'recent'
    else:
        signal['freshness'] = 'old'
    
    return signal


if __name__ == "__main__":
    # Test advanced scoring
    test_signal = {
        'id': 'test-1',
        'title': 'Dragonfly: Redis Alternative 25x Faster',
        'description': 'A drop-in Redis replacement built in C++',
        'source': 'Dan Luu',
        'published_at': (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
        'metadata': {'stars': 12000}
    }
    
    user_stack = {
        'languages': ['python'],
        'databases': ['redis', 'postgres']
    }
    
    enriched = enrich_signal(test_signal, user_stack)
    
    print("Advanced Scoring Test")
    print("=" * 60)
    print(f"Signal: {test_signal['title']}")
    print(f"Base score: {test_signal.get('score', 50)}")
    print(f"Advanced score: {enriched['advanced_score']}")
    print(f"Detected tech: {enriched['detected_tech']}")
    print(f"Is expert: {enriched['is_expert']}")
    print(f"Freshness: {enriched['freshness']}")
    print("=" * 60)
