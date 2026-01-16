"""
CSO.ai Storage Layer.

Persistent storage for:
- Intelligence profiles
- Articles and content
- Insights and recommendations

Storage Backends:
- SQLite (local): For offline/development use
- Supabase (cloud): For production with tenant isolation
"""

from cso_ai.storage.database import Database
from cso_ai.storage.supabase_client import (
    Article,
    Insight,
    SupabaseClient,
    TenantContext,
)

__all__ = [
    "Database",
    "SupabaseClient",
    "TenantContext",
    "Article",
    "Insight",
]
