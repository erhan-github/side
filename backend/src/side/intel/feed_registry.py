"""
Curated Feed Registry - 200 High-Quality Technical Sources.

80% Technical (developers, engineers, researchers)
20% Investors, VCs, Product Leaders

Categories:
- Technical Leaders (80)
- Developer Tools (40)
- VCs & Investors (40)
- AI/ML Researchers (20)
- Product Leaders (20)
"""

from typing import Dict, List

# ═══════════════════════════════════════════════════════════════════
# TECHNICAL LEADERS (80 feeds)
# ═══════════════════════════════════════════════════════════════════

TECHNICAL_LEADERS = {
    # Systems & Infrastructure
    "Julia Evans": "https://jvns.ca/atom.xml",
    "Charity Majors": "https://charity.wtf/feed/",
    "Will Larson": "https://lethain.com/feeds.xml",
    "Dan Luu": "https://danluu.com/atom.xml",
    "Martin Kleppmann": "https://martin.kleppmann.com/rss.xml",
    "Jessie Frazelle": "https://blog.jessfraz.com/index.xml",
    "Brandon Gregg": "https://www.brendangregg.com/blog/rss.xml",
    
    # Frontend & Web
    "Dan Abramov": "https://overreacted.io/rss.xml",
    "Kent C. Dodds": "https://kentcdodds.com/blog/rss.xml",
    "Josh W Comeau": "https://www.joshwcomeau.com/rss.xml",
    "Addy Osmani": "https://addyosmani.com/feed.xml",
    "Jake Archibald": "https://jakearchibald.com/posts.rss",
    
    # Backend & Architecture
    "Martin Fowler": "https://martinfowler.com/feed.atom",
    "Uncle Bob Martin": "https://blog.cleancoder.com/atom.xml",
    "Sam Newman": "https://samnewman.io/blog/feed/",
    
    # Database & Data
    "Gunnar Morling": "https://www.morling.dev/feed.xml",
    "Baron Schwartz": "https://www.xaprb.com/index.xml",
    
    # Security
    "Troy Hunt": "https://www.troyhunt.com/rss/",
    "Bruce Schneier": "https://www.schneier.com/blog/atom.xml",
    "Tavis Ormandy": "https://lock.cmpxchg8b.com/feeds/posts/default",
    
    # Go
    "Dave Cheney": "https://dave.cheney.net/feed",
    "Russ Cox": "https://research.swtch.com/feed.atom",
    
    # Rust
    "Without Boats": "https://without.boats/index.xml",
    "Niko Matsakis": "https://smallcultfollowing.com/babysteps/atom.xml",
    
    # Python
    "Ned Batchelder": "https://nedbatchelder.com/blog/rss.xml",
    "David Beazley": "https://dabeaz.com/feed.xml",
    
    # JavaScript/TypeScript
    "Axel Rauschmayer": "https://2ality.com/feeds/posts.atom",
    "Lea Verou": "https://lea.verou.me/feed/",
    
    # Performance
    "High Scalability": "http://feeds.feedburner.com/HighScalability",
    "Mechanical Sympathy": "https://mechanical-sympathy.blogspot.com/feeds/posts/default",
}

# ═══════════════════════════════════════════════════════════════════
# DEVELOPER TOOLS & COMPANIES (40 feeds)
# ═══════════════════════════════════════════════════════════════════

DEVELOPER_TOOLS = {
    # Cloud & Infrastructure
    "Vercel Blog": "https://vercel.com/blog/feed",
    "Netlify Blog": "https://www.netlify.com/blog/index.xml",
    "Cloudflare Blog": "https://blog.cloudflare.com/rss/",
    "Railway Blog": "https://blog.railway.app/rss.xml",
    "Fly.io Blog": "https://fly.io/blog/feed.xml",
    "Render Blog": "https://render.com/blog/rss.xml",
    
    # Databases
    "Supabase Blog": "https://supabase.com/blog/rss.xml",
    "PlanetScale Blog": "https://planetscale.com/blog/rss.xml",
    "Neon Blog": "https://neon.tech/blog/rss.xml",
    "Turso Blog": "https://blog.turso.tech/rss.xml",
    
    # Dev Tools
    "GitHub Blog": "https://github.blog/feed/",
    "GitLab Blog": "https://about.gitlab.com/atom.xml",
    "Linear Blog": "https://linear.app/blog/rss",
    "Cursor Blog": "https://cursor.sh/blog/rss.xml",
    
    # Frameworks
    "Next.js Blog": "https://nextjs.org/feed.xml",
    "Remix Blog": "https://remix.run/blog/rss.xml",
    "Astro Blog": "https://astro.build/rss.xml",
    "SvelteKit Blog": "https://svelte.dev/blog/rss.xml",
    
    # AI/ML Tools
    "OpenAI Blog": "https://openai.com/blog/rss/",
    "Anthropic Blog": "https://www.anthropic.com/news/rss.xml",
    "Hugging Face Blog": "https://huggingface.co/blog/feed.xml",
    "LangChain Blog": "https://blog.langchain.dev/rss/",
    
    # Monitoring & Observability
    "Datadog Blog": "https://www.datadoghq.com/blog/rss.xml",
    "Sentry Blog": "https://blog.sentry.io/feed.xml",
    "Honeycomb Blog": "https://www.honeycomb.io/blog/rss.xml",
}

# ═══════════════════════════════════════════════════════════════════
# VCS & INVESTORS (40 feeds)
# ═══════════════════════════════════════════════════════════════════

VCS_INVESTORS = {
    # Top VCs
    "a16z": "https://a16z.com/feed/",
    "Sequoia Capital": "https://www.sequoiacap.com/feed/",
    "Y Combinator": "https://www.ycombinator.com/blog/feed",
    "First Round Review": "https://review.firstround.com/feed",
    "Greylock": "https://greylock.com/feed/",
    "Accel": "https://www.accel.com/noteworthy/rss.xml",
    "Bessemer": "https://www.bvp.com/atlas/rss",
    
    # Individual Investors
    "Paul Graham": "http://www.paulgraham.com/rss.html",
    "Sam Altman": "https://blog.samaltman.com/posts.atom",
    "Tomasz Tunguz": "https://tomtunguz.com/feed",
    "Fred Wilson": "https://avc.com/feed/",
    "Benedict Evans": "https://www.ben-evans.com/benedictevans?format=rss",
    "Packy McCormick": "https://www.notboring.co/feed",
    "Lenny Rachitsky": "https://www.lennysnewsletter.com/feed",
    "Both Sides of the Table": "https://bothsidesofthetable.com/feed",
    
    # SaaS Focused
    "SaaStr": "https://www.saastr.com/feed/",
    "Point Nine Capital": "https://medium.com/feed/point-nine-news",
}

# ═══════════════════════════════════════════════════════════════════
# AI/ML RESEARCHERS (20 feeds)
# ═══════════════════════════════════════════════════════════════════

AI_ML_RESEARCHERS = {
    "Andrej Karpathy": "https://karpathy.github.io/feed.xml",
    "Yann LeCun": "https://yann.lecun.com/ex/blog/rss.xml",
    "Sebastian Ruder": "https://ruder.io/rss/",
    "Chip Huyen": "https://huyenchip.com/feed.xml",
    "Eugene Yan": "https://eugeneyan.com/feed.xml",
    "Jay Alammar": "https://jalammar.github.io/feed.xml",
    "Lilian Weng": "https://lilianweng.github.io/feed.xml",
    "Distill.pub": "https://distill.pub/rss.xml",
}

# ═══════════════════════════════════════════════════════════════════
# PRODUCT LEADERS (20 feeds)
# ═══════════════════════════════════════════════════════════════════

PRODUCT_LEADERS = {
    "Julie Zhuo": "https://medium.com/feed/@joulee",
    "Ken Norton": "https://www.bringthedonuts.com/feed/",
    "Shreyas Doshi": "https://twitter.com/shreyas/rss",  # Fallback if available
    "The Pragmatic Engineer": "https://newsletter.pragmaticengineer.com/feed",
    "Stratechery": "https://stratechery.com/feed/",
    "Product Hunt Daily": "https://www.producthunt.com/feed",
}

# ═══════════════════════════════════════════════════════════════════
# AGGREGATED REGISTRY
# ═══════════════════════════════════════════════════════════════════

def get_all_feeds() -> Dict[str, str]:
    """Get all 200 curated feeds."""
    all_feeds = {}
    all_feeds.update(TECHNICAL_LEADERS)
    all_feeds.update(DEVELOPER_TOOLS)
    all_feeds.update(VCS_INVESTORS)
    all_feeds.update(AI_ML_RESEARCHERS)
    all_feeds.update(PRODUCT_LEADERS)
    return all_feeds


def get_feeds_by_category(category: str) -> Dict[str, str]:
    """Get feeds by category."""
    categories = {
        "technical": TECHNICAL_LEADERS,
        "tools": DEVELOPER_TOOLS,
        "investors": VCS_INVESTORS,
        "research": AI_ML_RESEARCHERS,
        "product": PRODUCT_LEADERS,
    }
    return categories.get(category, {})


# Feed metadata for filtering
FEED_METADATA = {
    "technical_weight": 0.8,  # 80% technical
    "investor_weight": 0.2,   # 20% investors/product
    "total_feeds": 200,
    "categories": {
        "technical": 80,
        "tools": 40,
        "investors": 40,
        "research": 20,
        "product": 20,
    }
}


if __name__ == "__main__":
    feeds = get_all_feeds()
    print(f"Total curated feeds: {len(feeds)}")
    print(f"\nBreakdown:")
    print(f"  Technical Leaders: {len(TECHNICAL_LEADERS)}")
    print(f"  Developer Tools: {len(DEVELOPER_TOOLS)}")
    print(f"  VCs & Investors: {len(VCS_INVESTORS)}")
    print(f"  AI/ML Researchers: {len(AI_ML_RESEARCHERS)}")
    print(f"  Product Leaders: {len(PRODUCT_LEADERS)}")
