"""
CSO.ai Embeddings - Vector embeddings for semantic search.

This module handles generating embeddings for articles and queries,
enabling semantic similarity search in the Supabase pgvector database.

Embedding Strategy:
- Use a lightweight model that runs locally (no API costs)
- 384-dimensional embeddings (MiniLM-L6-v2 compatible)
- Fall back to keyword-based search if embeddings unavailable
"""

import hashlib
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class EmbeddingResult:
    """Result of an embedding operation."""
    
    text: str
    embedding: list[float]
    model: str
    dimensions: int


class EmbeddingProvider:
    """
    Generates text embeddings for semantic search.
    
    Uses Hugging Face's free inference API by default.
    Can be configured to use local models or other providers.
    """
    
    # Free Hugging Face inference API (rate limited but sufficient for dev)
    HF_API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/"
    
    # Model: all-MiniLM-L6-v2 - Fast, 384 dimensions, good for semantic search
    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    def __init__(
        self,
        model: str | None = None,
        hf_token: str | None = None,
    ) -> None:
        """
        Initialize the embedding provider.
        
        Args:
            model: Model to use for embeddings (default: all-MiniLM-L6-v2)
            hf_token: Hugging Face API token (optional, increases rate limits)
        """
        self.model = model or self.DEFAULT_MODEL
        self.hf_token = hf_token
        self._client: httpx.AsyncClient | None = None
        self._cache: dict[str, list[float]] = {}
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    def _cache_key(self, text: str) -> str:
        """Generate a cache key for text."""
        return hashlib.md5(text.encode()).hexdigest()
    
    async def embed_text(self, text: str) -> list[float] | None:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            384-dimensional embedding vector, or None if failed
        """
        if not text or not text.strip():
            return None
        
        # Check cache
        cache_key = self._cache_key(text)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Truncate long text (model has 512 token limit)
        text = text[:2000]
        
        try:
            client = await self._get_client()
            
            headers = {"Content-Type": "application/json"}
            if self.hf_token:
                headers["Authorization"] = f"Bearer {self.hf_token}"
            
            response = await client.post(
                f"{self.HF_API_URL}{self.model}",
                headers=headers,
                json={"inputs": text, "options": {"wait_for_model": True}},
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list):
                    if isinstance(result[0], float):
                        # Already a flat list
                        embedding = result
                    elif isinstance(result[0], list):
                        # Nested list - take first
                        embedding = result[0]
                    else:
                        return None
                else:
                    return None
                
                # Cache the result
                self._cache[cache_key] = embedding
                
                return embedding
            
            # Handle rate limiting
            if response.status_code == 503:
                # Model is loading, could retry
                return None
            
            return None
            
        except Exception:
            return None
    
    async def embed_texts(self, texts: list[str]) -> list[list[float] | None]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embeddings (same order as input), None for failed ones
        """
        results: list[list[float] | None] = []
        
        # Process in batches to avoid rate limits
        batch_size = 10
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            for text in batch:
                embedding = await self.embed_text(text)
                results.append(embedding)
        
        return results
    
    async def embed_article(self, title: str, description: str | None = None) -> list[float] | None:
        """
        Generate embedding for an article.
        
        Combines title and description for richer embedding.
        """
        text = title
        if description:
            text = f"{title}. {description[:500]}"
        
        return await self.embed_text(text)
    
    def cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Returns value between -1 and 1 (1 = identical).
        """
        if len(a) != len(b):
            return 0.0
        
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def find_similar(
        self,
        query_embedding: list[float],
        embeddings: list[tuple[str, list[float]]],
        top_k: int = 10,
        threshold: float = 0.5,
    ) -> list[tuple[str, float]]:
        """
        Find most similar items to a query embedding.
        
        Args:
            query_embedding: The query vector
            embeddings: List of (id, embedding) tuples to search
            top_k: Maximum results to return
            threshold: Minimum similarity score
            
        Returns:
            List of (id, similarity_score) tuples, sorted by score descending
        """
        scores: list[tuple[str, float]] = []
        
        for item_id, embedding in embeddings:
            similarity = self.cosine_similarity(query_embedding, embedding)
            if similarity >= threshold:
                scores.append((item_id, similarity))
        
        # Sort by similarity descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores[:top_k]


# Singleton instance
_embedding_provider: EmbeddingProvider | None = None


def get_embedding_provider() -> EmbeddingProvider:
    """Get or create the embedding provider singleton."""
    global _embedding_provider
    if _embedding_provider is None:
        _embedding_provider = EmbeddingProvider()
    return _embedding_provider


async def embed_text(text: str) -> list[float] | None:
    """Convenience function to embed text."""
    provider = get_embedding_provider()
    return await provider.embed_text(text)


async def embed_article(title: str, description: str | None = None) -> list[float] | None:
    """Convenience function to embed an article."""
    provider = get_embedding_provider()
    return await provider.embed_article(title, description)
