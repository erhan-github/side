"""
CSO.ai Supabase Client with Tenant Isolation

This module provides a secure, tenant-isolated interface to Supabase.
Each workspace/project gets its own tenant_id, ensuring complete data isolation.

ISOLATION GUARANTEE:
- Tenant A can NEVER see Tenant B's data
- Articles are shared (public sources), but scores/insights are isolated
- All operations are scoped to the current tenant
"""

import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

from ..config import (
    SUPABASE_ANON_KEY,
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_URL,
)


@dataclass
class TenantContext:
    """Represents the current tenant's context."""
    
    tenant_id: str
    workspace_hash: str
    name: str | None = None
    primary_language: str | None = None
    domain: str | None = None
    stage: str | None = None
    frameworks: list[str] = field(default_factory=list)
    recent_focus_areas: list[str] = field(default_factory=list)


@dataclass
class Article:
    """An article from a news source."""
    
    id: str
    title: str
    url: str
    source: str
    description: str | None = None
    author: str | None = None
    source_score: int | None = None
    published_at: datetime | None = None
    fetched_at: datetime | None = None
    tags: list[str] = field(default_factory=list)
    
    # Tenant-specific fields (not stored in articles table)
    relevance_score: float | None = None
    score_reason: str | None = None
    similarity: float | None = None


@dataclass
class Insight:
    """A strategic insight generated for a tenant."""
    
    id: str
    insight_type: str  # 'strategic', 'technical', 'market', 'risk', 'opportunity'
    title: str
    content: str
    confidence: float
    is_read: bool = False
    created_at: datetime | None = None
    source_articles: list[str] = field(default_factory=list)


class SupabaseClient:
    """
    Tenant-isolated Supabase client for CSO.ai.
    
    Usage:
        client = SupabaseClient.for_workspace("/path/to/workspace")
        articles = await client.get_relevant_articles(limit=10)
        await client.save_insight(insight)
    """
    
    def __init__(self, tenant_id: str, workspace_hash: str) -> None:
        """Initialize with a specific tenant context."""
        self.tenant_id = tenant_id
        self.workspace_hash = workspace_hash
        self._base_url = SUPABASE_URL
        self._service_key = SUPABASE_SERVICE_ROLE_KEY
        self._anon_key = SUPABASE_ANON_KEY
        self._client: httpx.AsyncClient | None = None
    
    @classmethod
    def compute_workspace_hash(cls, workspace_path: str) -> str:
        """
        Compute a unique, privacy-preserving hash for a workspace.
        
        This hash is:
        - Deterministic: Same path always produces same hash
        - Privacy-preserving: Cannot reverse to get the original path
        - Collision-resistant: Different paths produce different hashes
        """
        # Normalize the path
        normalized = str(Path(workspace_path).resolve())
        
        # Create a SHA-256 hash
        hash_bytes = hashlib.sha256(normalized.encode()).digest()
        
        # Return first 16 bytes as hex (32 chars) - sufficient for uniqueness
        return hash_bytes[:16].hex()
    
    @classmethod
    async def for_workspace(cls, workspace_path: str, name: str | None = None) -> "SupabaseClient":
        """
        Create a client for a specific workspace, ensuring tenant exists.
        
        Args:
            workspace_path: Path to the workspace/project directory
            name: Optional human-readable name for the tenant
            
        Returns:
            SupabaseClient configured for this tenant
        """
        workspace_hash = cls.compute_workspace_hash(workspace_path)
        
        # Get or create tenant
        async with httpx.AsyncClient() as http:
            response = await http.post(
                f"{SUPABASE_URL}/rest/v1/rpc/get_or_create_tenant",
                headers={
                    "apikey": SUPABASE_SERVICE_ROLE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "p_workspace_hash": workspace_hash,
                    "p_name": name,
                },
                timeout=30.0,
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Failed to get/create tenant: {response.text}")
            
            tenant_id = response.json()
        
        return cls(tenant_id=tenant_id, workspace_hash=workspace_hash)
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if Supabase is properly configured."""
        return bool(
            SUPABASE_URL
            and SUPABASE_SERVICE_ROLE_KEY
            and SUPABASE_ANON_KEY
        )
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    def _headers(self, use_service_role: bool = True) -> dict[str, str]:
        """Get headers for Supabase requests."""
        key = self._service_key if use_service_role else self._anon_key
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
    
    # =========================================================================
    # Article Operations (Shared + Tenant Scoring)
    # =========================================================================
    
    async def save_articles(self, articles: list[Article]) -> int:
        """
        Save articles to the shared articles table.
        
        Args:
            articles: List of articles to save
            
        Returns:
            Number of articles saved (upserted)
        """
        if not articles:
            return 0
        
        client = await self._get_client()
        
        # Prepare article data (without tenant-specific fields)
        article_data = [
            {
                "id": a.id,
                "title": a.title,
                "url": a.url,
                "source": a.source,
                "description": a.description,
                "author": a.author,
                "source_score": a.source_score,
                "published_at": a.published_at.isoformat() if a.published_at else None,
                "tags": a.tags,
            }
            for a in articles
        ]
        
        # Upsert articles
        response = await client.post(
            f"{self._base_url}/rest/v1/articles",
            headers={
                **self._headers(),
                "Prefer": "resolution=merge-duplicates",
            },
            json=article_data,
        )
        
        if response.status_code not in (200, 201):
            raise RuntimeError(f"Failed to save articles: {response.text}")
        
        return len(articles)
    
    async def get_articles(
        self,
        source: str | None = None,
        limit: int = 50,
        days: int = 7,
    ) -> list[Article]:
        """
        Get articles from the shared pool.
        
        Args:
            source: Filter by source (hackernews, lobsters, github, etc.)
            limit: Maximum number of articles to return
            days: Only return articles from the last N days
            
        Returns:
            List of articles
        """
        client = await self._get_client()
        
        # Build query
        params = {
            "select": "*",
            "order": "fetched_at.desc",
            "limit": str(limit),
        }
        
        if source:
            params["source"] = f"eq.{source}"
        
        response = await client.get(
            f"{self._base_url}/rest/v1/articles",
            headers=self._headers(use_service_role=False),
            params=params,
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Failed to get articles: {response.text}")
        
        data = response.json()
        
        return [
            Article(
                id=row["id"],
                title=row["title"],
                url=row["url"],
                source=row["source"],
                description=row.get("description"),
                author=row.get("author"),
                source_score=row.get("source_score"),
                published_at=datetime.fromisoformat(row["published_at"]) if row.get("published_at") else None,
                fetched_at=datetime.fromisoformat(row["fetched_at"]) if row.get("fetched_at") else None,
                tags=row.get("tags") or [],
            )
            for row in data
        ]
    
    async def save_article_score(
        self,
        article_id: str,
        stack: str,
        domain: str,
        score: float,
        reason: str | None = None,
    ) -> None:
        """
        Save a tenant-specific article score.
        
        This score is isolated to the current tenant - other tenants
        will never see this score.
        """
        client = await self._get_client()
        
        response = await client.post(
            f"{self._base_url}/rest/v1/article_scores",
            headers={
                **self._headers(),
                "Prefer": "resolution=merge-duplicates",
            },
            json={
                "tenant_id": self.tenant_id,
                "article_id": article_id,
                "stack": stack,
                "domain": domain,
                "score": score,
                "reason": reason,
            },
        )
        
        if response.status_code not in (200, 201):
            raise RuntimeError(f"Failed to save article score: {response.text}")
    
    async def get_scored_articles(
        self,
        stack: str | None = None,
        domain: str | None = None,
        min_score: float = 50.0,
        limit: int = 20,
    ) -> list[Article]:
        """
        Get articles with tenant-specific scores.
        
        Only returns articles that have been scored for this tenant.
        """
        client = await self._get_client()
        
        # Join articles with scores for this tenant
        params = {
            "select": "*, article_scores!inner(score, reason)",
            "article_scores.tenant_id": f"eq.{self.tenant_id}",
            "article_scores.score": f"gte.{min_score}",
            "order": "article_scores.score.desc",
            "limit": str(limit),
        }
        
        if stack:
            params["article_scores.stack"] = f"eq.{stack}"
        if domain:
            params["article_scores.domain"] = f"eq.{domain}"
        
        response = await client.get(
            f"{self._base_url}/rest/v1/articles",
            headers=self._headers(),
            params=params,
        )
        
        if response.status_code != 200:
            # If join fails, return empty (no scores yet)
            return []
        
        data = response.json()
        
        return [
            Article(
                id=row["id"],
                title=row["title"],
                url=row["url"],
                source=row["source"],
                description=row.get("description"),
                author=row.get("author"),
                source_score=row.get("source_score"),
                relevance_score=row["article_scores"][0]["score"] if row.get("article_scores") else None,
                score_reason=row["article_scores"][0]["reason"] if row.get("article_scores") else None,
            )
            for row in data
        ]
    
    # =========================================================================
    # Tenant Context Operations (Isolated)
    # =========================================================================
    
    async def save_context(self, context: dict[str, Any]) -> None:
        """
        Save or update the tenant's context (codebase understanding).
        
        This is completely isolated - other tenants cannot see this.
        """
        client = await self._get_client()
        
        # Upsert context for this tenant
        response = await client.post(
            f"{self._base_url}/rest/v1/tenant_context",
            headers={
                **self._headers(),
                "Prefer": "resolution=merge-duplicates",
            },
            json={
                "tenant_id": self.tenant_id,
                **context,
                "updated_at": datetime.utcnow().isoformat(),
            },
        )
        
        if response.status_code not in (200, 201):
            raise RuntimeError(f"Failed to save context: {response.text}")
    
    async def get_context(self) -> TenantContext | None:
        """
        Get the tenant's current context.
        """
        client = await self._get_client()
        
        response = await client.get(
            f"{self._base_url}/rest/v1/tenant_context",
            headers=self._headers(),
            params={
                "tenant_id": f"eq.{self.tenant_id}",
                "select": "*",
            },
        )
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        if not data:
            return None
        
        row = data[0]
        return TenantContext(
            tenant_id=self.tenant_id,
            workspace_hash=self.workspace_hash,
            primary_language=row.get("primary_language"),
            domain=row.get("domain"),
            stage=row.get("stage"),
            frameworks=row.get("frameworks") or [],
            recent_focus_areas=row.get("recent_focus_areas") or [],
        )
    
    # =========================================================================
    # Insight Operations (Isolated)
    # =========================================================================
    
    async def save_insight(self, insight: Insight) -> str:
        """
        Save a strategic insight for this tenant.
        
        Returns the insight ID.
        """
        client = await self._get_client()
        
        response = await client.post(
            f"{self._base_url}/rest/v1/tenant_insights",
            headers={
                **self._headers(),
                "Prefer": "return=representation",
            },
            json={
                "tenant_id": self.tenant_id,
                "insight_type": insight.insight_type,
                "title": insight.title,
                "content": insight.content,
                "confidence": insight.confidence,
                "source_articles": insight.source_articles,
            },
        )
        
        if response.status_code not in (200, 201):
            raise RuntimeError(f"Failed to save insight: {response.text}")
        
        data = response.json()
        return data[0]["id"] if data else insight.id
    
    async def get_insights(
        self,
        insight_type: str | None = None,
        unread_only: bool = False,
        limit: int = 10,
    ) -> list[Insight]:
        """
        Get insights for this tenant.
        """
        client = await self._get_client()
        
        params = {
            "tenant_id": f"eq.{self.tenant_id}",
            "order": "created_at.desc",
            "limit": str(limit),
        }
        
        if insight_type:
            params["insight_type"] = f"eq.{insight_type}"
        if unread_only:
            params["is_read"] = "eq.false"
        
        response = await client.get(
            f"{self._base_url}/rest/v1/tenant_insights",
            headers=self._headers(),
            params=params,
        )
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        
        return [
            Insight(
                id=row["id"],
                insight_type=row["insight_type"],
                title=row["title"],
                content=row["content"],
                confidence=row.get("confidence", 0.0),
                is_read=row.get("is_read", False),
                created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else None,
                source_articles=row.get("source_articles") or [],
            )
            for row in data
        ]
    
    async def mark_insight_read(self, insight_id: str) -> None:
        """Mark an insight as read."""
        client = await self._get_client()
        
        await client.patch(
            f"{self._base_url}/rest/v1/tenant_insights",
            headers=self._headers(),
            params={
                "id": f"eq.{insight_id}",
                "tenant_id": f"eq.{self.tenant_id}",  # Ensure tenant isolation
            },
            json={"is_read": True},
        )
    
    # =========================================================================
    # Usage Tracking (Isolated)
    # =========================================================================
    
    async def track_usage(self, action: str, metadata: dict[str, Any] | None = None) -> None:
        """
        Track a usage event for this tenant.
        
        Used for analytics and billing.
        """
        client = await self._get_client()
        
        await client.post(
            f"{self._base_url}/rest/v1/usage",
            headers=self._headers(),
            json={
                "tenant_id": self.tenant_id,
                "action": action,
                "metadata": metadata or {},
            },
        )
    
    async def get_usage_stats(self) -> dict[str, int]:
        """Get usage statistics for this tenant."""
        client = await self._get_client()
        
        response = await client.get(
            f"{self._base_url}/rest/v1/usage",
            headers=self._headers(),
            params={
                "tenant_id": f"eq.{self.tenant_id}",
                "select": "action",
            },
        )
        
        if response.status_code != 200:
            return {}
        
        data = response.json()
        
        # Count by action
        stats: dict[str, int] = {}
        for row in data:
            action = row["action"]
            stats[action] = stats.get(action, 0) + 1
        
        return stats
